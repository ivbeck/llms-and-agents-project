from src.tui.cli import build_parser

def test_parser_builds():
    parser = build_parser()
    assert parser is not None