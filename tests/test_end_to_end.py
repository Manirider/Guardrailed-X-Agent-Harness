import tempfile
from pathlib import Path
from datetime import date

from src.harness.scheduler import select_due_row
from src.harness.guardrails import GuardrailChain


def test_e2e_flow():
    # minimal flow test without browser
    import csv
    td = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv")
    writer = csv.writer(td)
    writer.writerow(["row_id","post_date","raw_text"])
    writer.writerow(["r1", "2026-10-03", "hello"])
    td.close()
    path = Path(td.name)
    sel,_ ,_ = select_due_row(path, today=date(2026,10,3), posted_ids=set())
    assert sel.row_id == "r1"
    g = GuardrailChain()
    res = g.check(sel.raw_text, sel.raw_text)
    assert res.passed
