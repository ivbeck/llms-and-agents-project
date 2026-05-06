"""Lightweight performance instrumentation for pipeline runs."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Iterator

from src.models import LLMCallUsage, PerformanceReport, PerformanceSpan, TokenUsage

logger = logging.getLogger(__name__)


class PerformanceTracker:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self._started_at = time.perf_counter()
        self._spans: list[PerformanceSpan] = []
        self._llm_calls: list[LLMCallUsage] = []

    @contextmanager
    def span(self, name: str, **metadata: Any) -> Iterator[dict[str, Any]]:
        if not self.enabled:
            yield metadata
            return

        started_at = time.perf_counter()
        span_metadata = dict(metadata)
        try:
            yield span_metadata
        except Exception:
            span_metadata["error"] = True
            raise
        finally:
            duration_ms = (time.perf_counter() - started_at) * 1000
            self._spans.append(
                PerformanceSpan(
                    name=name,
                    duration_ms=round(duration_ms, 2),
                    metadata=span_metadata,
                )
            )

    def record_llm_call(self, usage: LLMCallUsage) -> None:
        self._llm_calls.append(usage)

    def token_usage(self) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=sum(call.prompt_tokens for call in self._llm_calls),
            completion_tokens=sum(call.completion_tokens for call in self._llm_calls),
            total_tokens=sum(call.total_tokens for call in self._llm_calls),
            reasoning_tokens=sum(call.reasoning_tokens for call in self._llm_calls),
            calls=len(self._llm_calls),
        )

    def finish(self) -> PerformanceReport | None:
        if not self.enabled and not self._llm_calls:
            return None

        total_duration_ms = (time.perf_counter() - self._started_at) * 1000
        return PerformanceReport(
            total_duration_ms=round(total_duration_ms, 2),
            spans=self._spans if self.enabled else [],
            token_usage=self.token_usage(),
            llm_calls=self._llm_calls,
        )


def log_performance_report(report: PerformanceReport | None) -> None:
    if report is None:
        return

    logger.info("Performance analysis: total %.2f ms", report.total_duration_ms)
    logger.info(
        "Token usage: total=%d, prompt=%d, completion=%d, reasoning=%d, calls=%d",
        report.token_usage.total_tokens,
        report.token_usage.prompt_tokens,
        report.token_usage.completion_tokens,
        report.token_usage.reasoning_tokens,
        report.token_usage.calls,
    )
    for span in sorted(report.spans, key=lambda item: item.duration_ms, reverse=True):
        details = ", ".join(f"{key}={value}" for key, value in span.metadata.items())
        logger.info("PERF | %9.2f ms | %s%s", span.duration_ms, span.name, f" | {details}" if details else "")
