import tempfile
from datetime import date
from pathlib import Path

from src.harness.scheduler import select_due_row


def make_csv(rows):
    import csv
    f = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="")
    writer = csv.writer(f)
    writer.writerow(["row_id","post_date","raw_text"])
    for r in rows:
        writer.writerow(r)
    f.close()
    return Path(f.name)


def test_todays_row_selected():
    path = make_csv([("r1","2026-10-03","text")])
    sel, ignored, multiple = select_due_row(path, today=date(2026,10,3), posted_ids=set())
    assert sel.row_id == "r1"
    assert not multiple

def test_tomorrow_ignored():
    path = make_csv([("r1","2026-10-04","text")])
    sel, _, _ = select_due_row(path, today=date(2026,10,3), posted_ids=set())
    assert sel is None

def test_posted_row_ignored():
    path = make_csv([("r1","2026-10-03","text")])
    sel, _, _ = select_due_row(path, today=date(2026,10,3), posted_ids={"r1"})
    assert sel is None

def test_multiple_due_rows():
    path = make_csv([("r2","2026-10-03","t2"),("r1","2026-10-03","t1")])
    sel, ignored, multiple = select_due_row(path, today=date(2026,10,3), posted_ids=set())
    assert sel.row_id == "r1"
    assert multiple
    assert ignored == ["r2"]
