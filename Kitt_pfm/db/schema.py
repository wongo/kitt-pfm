"""Database schema as a Python string, loaded from schema.sql."""
from pathlib import Path

SCHEMA = Path(__file__).parent.joinpath("schema.sql").read_text(encoding="utf-8")
