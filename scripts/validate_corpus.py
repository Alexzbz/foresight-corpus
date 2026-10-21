#!/usr/bin/env python3
"""Validate the foresight-corpus snapshot. Stdlib only — runs in CI.

Checks the same invariants the skill's gates enforce on run ledgers:
- every evidence row is uniquely keyed, has a claim, and is locatable
  (excerpt or locator present);
- retrieved_at timestamps are real ISO-8601 instants, not placeholders;
- domains/geography parse as JSON arrays with at least one domain;
- the FTS index covers every evidence row;
- the per-domain JSONL exports stay in sync with the database;
- corpus-meta.json matches the database it ships next to.
"""
import hashlib
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "corpus" / "corpus.db"
META = ROOT / "corpus" / "corpus-meta.json"
EXPORTS = ROOT / "corpus" / "evidence"


def main() -> int:
    errors: list[str] = []
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    evidence = [dict(r) for r in conn.execute("SELECT * FROM evidence")]
    sources = [dict(r) for r in conn.execute("SELECT * FROM sources")]
    meta_db = dict(conn.execute("SELECT key, value FROM corpus_meta"))
    fts_rows = conn.execute(
        "SELECT e.corpus_id FROM evidence e "
        "LEFT JOIN evidence_fts ON e.rowid = evidence_fts.rowid "
        "WHERE evidence_fts.rowid IS NULL"
    ).fetchall()
    conn.close()

    if fts_rows:
        errors.append(f"FTS index missing for {len(fts_rows)} evidence rows "
                      f"(first: {fts_rows[0]['corpus_id']})")

    ids = [r["corpus_id"] for r in evidence]
    if len(ids) != len(set(ids)):
        errors.append("duplicate corpus_id values in evidence")
    if len(sources) != len({s["source_id"] for s in sources}):
        errors.append("duplicate source_id values in sources")

    for r in evidence:
        cid = r["corpus_id"]
        if not (r["claim"] or "").strip():
            errors.append(f"{cid}: empty claim")
        if not (r["excerpt"] or "").strip() and not (r["locator"] or "").strip():
            errors.append(f"{cid}: neither excerpt nor locator — not traceable")
        retrieved = r["retrieved_at"] or ""
        try:
            from datetime import datetime
            datetime.fromisoformat(retrieved.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{cid}: retrieved_at is not an ISO instant: {retrieved!r}")
        try:
            domains = json.loads(r["domains"] or "[]")
            if not domains:
                errors.append(f"{cid}: no domain assigned")
        except json.JSONDecodeError:
            errors.append(f"{cid}: domains is not valid JSON")

    exported: set[str] = set()
    export_files = sorted(p for p in EXPORTS.glob("*.jsonl") if p.name != "sources.jsonl")
    for path in export_files:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"{path.name}:{i}: invalid JSON")
                continue
            exported.add(row.get("corpus_id", ""))
    missing = set(ids) - exported
    extra = exported - set(ids)
    if missing:
        errors.append(f"{len(missing)} evidence rows missing from JSONL exports "
                      f"(first: {sorted(missing)[0]})")
    if extra:
        errors.append(f"JSONL exports contain unknown ids (first: {sorted(extra)[0]})")

    exported_sources: set[str] = set()
    sources_file = EXPORTS / "sources.jsonl"
    for i, line in enumerate(sources_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"sources.jsonl:{i}: invalid JSON")
            continue
        exported_sources.add(row.get("source_id", ""))
    if exported_sources != {s["source_id"] for s in sources}:
        errors.append("sources.jsonl is out of sync with the database")

    manifest = json.loads(META.read_text(encoding="utf-8"))
    if manifest.get("evidence") != len(evidence):
        errors.append(f"corpus-meta.json evidence count {manifest.get('evidence')} != db {len(evidence)}")
    if manifest.get("sources") != len(sources):
        errors.append(f"corpus-meta.json sources count {manifest.get('sources')} != db {len(sources)}")
    if manifest.get("corpus_version") != meta_db.get("corpus_version"):
        errors.append("corpus-meta.json version does not match the database")
    digest = hashlib.sha256(DB.read_bytes()).hexdigest()
    if manifest.get("db_sha256") != digest:
        errors.append("corpus-meta.json db_sha256 does not match corpus.db")

    print(f"corpus {meta_db.get('corpus_version')}: {len(evidence)} evidence, "
          f"{len(sources)} sources, {len(export_files)} export files")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAILED: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OK: all corpus integrity checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
