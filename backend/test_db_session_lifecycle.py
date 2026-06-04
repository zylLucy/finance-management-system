from pathlib import Path

source = Path(__file__).with_name("main.py").read_text(encoding="utf-8")
assert "next(get_db())" not in source
