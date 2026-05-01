"""CLI entrypoint for the advanced multi-agent RAG system."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.config import Settings
from src.logging_config import setup
from src.orchestrator import AdvancedMultiAgentRAGSystem


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Advanced OpenRouter + Tavily Multi-Agent RAG")
    parser.add_argument("question", type=str, help="Question to answer")
    parser.add_argument("--json", action="store_true", help="Print full result JSON")
    parser.add_argument("--save", type=Path, default=None, help="Optional path to save JSON result")
    parser.add_argument("--baseline", action="store_true", help="Disable all seven advanced add-ons")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")

    parser.add_argument("--disable-hybrid-retrieval", action="store_true")
    parser.add_argument("--disable-cross-encoder-reranking", action="store_true")
    parser.add_argument("--disable-query-decomposition", action="store_true")
    parser.add_argument("--disable-iterative-retrieval", action="store_true")
    parser.add_argument("--disable-self-rag", action="store_true")
    parser.add_argument("--disable-evidence-filtering", action="store_true")
    parser.add_argument("--disable-hyde", action="store_true")

    parser.add_argument(
        "--openrouter-model",
        type=str,
        default=None,
        help="OpenRouter model to use (default: from settings)",
    )
    parser.add_argument("--max-search-results", type=int, default=None)
    parser.add_argument("--top-k-chunks", type=int, default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    return parser


def apply_cli_overrides(settings: Settings, args: argparse.Namespace) -> Settings:
    if args.baseline:
        settings.enable_hybrid_retrieval = False
        settings.enable_cross_encoder_reranking = False
        settings.enable_query_decomposition = False
        settings.enable_iterative_retrieval = False
        settings.enable_self_rag = False
        settings.enable_evidence_filtering = False
        settings.enable_hyde = False

    if args.disable_hybrid_retrieval:
        settings.enable_hybrid_retrieval = False
    if args.disable_cross_encoder_reranking:
        settings.enable_cross_encoder_reranking = False
    if args.disable_query_decomposition:
        settings.enable_query_decomposition = False
    if args.disable_iterative_retrieval:
        settings.enable_iterative_retrieval = False
    if args.disable_self_rag:
        settings.enable_self_rag = False
    if args.disable_evidence_filtering:
        settings.enable_evidence_filtering = False
    if args.disable_hyde:
        settings.enable_hyde = False

    if args.openrouter_model is not None:
        settings.openrouter_model = args.openrouter_model

    if args.max_search_results is not None:
        settings.max_search_results = args.max_search_results
    if args.top_k_chunks is not None:
        settings.top_k_chunks = args.top_k_chunks
    if args.max_iterations is not None:
        settings.max_iterations = args.max_iterations

    return settings


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger = setup("src", level=args.log_level)
    settings = apply_cli_overrides(Settings(), args)
    logger.info("Starting RAG system with OpenRouter model: %s", settings.openrouter_model)
    system = AdvancedMultiAgentRAGSystem(settings)
    result = system.answer_question(args.question)
    result_json = result.model_dump()

    if args.save is not None:
        args.save.write_text(json.dumps(result_json, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        return

    print("=" * 88)
    print("QUESTION")
    print("=" * 88)
    print(result.question)
    print()

    print("=" * 88)
    print("FEATURES")
    print("=" * 88)
    for key, value in result.features.model_dump().items():
        print(f"{key}: {value}")
    print()

    print("=" * 88)
    print("QUERIES")
    print("=" * 88)
    for i, q in enumerate(result.queries, start=1):
        print(f"{i}. {q}")
    print()

    if result.hyde_document:
        print("=" * 88)
        print("HYDE DOCUMENT")
        print("=" * 88)
        print(result.hyde_document)
        print()

    print("=" * 88)
    print("ANSWER")
    print("=" * 88)
    print(result.answer)
    print()

    print("=" * 88)
    print("CRITIC")
    print("=" * 88)
    print(f"Grounded: {result.critic.is_grounded}")
    print(f"Relevant: {result.critic.is_relevant}")
    print(f"Needs revision: {result.critic.needs_revision}")
    print(f"Comment: {result.critic.comment}")
    print()

    print("=" * 88)
    print("SOURCES")
    print("=" * 88)
    for i, source in enumerate(result.sources, start=1):
        print(f"{i}. {source.title}")
        print(f"   URL: {source.url}")
    print()

    print("=" * 88)
    print("ITERATION LEDGER")
    print("=" * 88)
    for step in result.ledger:
        print(f"Iteration {step.iteration}: {step.summary}")
    print()


if __name__ == "__main__":
    main()
