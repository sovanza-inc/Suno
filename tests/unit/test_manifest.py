import json

from suno.data.manifest import read_manifest, split_filter, write_manifest


def test_roundtrip(tmp_path):
    path = tmp_path / "m.jsonl"
    entries = [
        {"id": "a", "source": "fleurs", "path": "/x.wav", "text": "ہیلو", "split": "train"},
        {"id": "b", "source": "fleurs", "path": "/y.wav", "text": "بائے", "split": "validation"},
    ]
    write_manifest(entries, path)
    assert read_manifest(path) == entries


def test_split_filter():
    entries = [
        {"split": "train", "text": "abc"},
        {"split": "train", "text": ""},          # empty, filtered
        {"split": "validation", "text": "def"},  # wrong split
        {"split": "train", "text": "xyz"},
    ]
    out = split_filter(entries, "train")
    assert len(out) == 2
    assert all(e["split"] == "train" and e["text"].strip() for e in out)


def test_read_missing(tmp_path):
    assert read_manifest(tmp_path / "missing.jsonl") == []


def test_unicode_preserved(tmp_path):
    path = tmp_path / "m.jsonl"
    entries = [{"id": "a", "text": "اردو ٹیسٹ ۱۲۳"}]
    write_manifest(entries, path)
    raw = path.read_text()
    assert "اردو" in raw  # ensure_ascii=False is set
    assert json.loads(raw.splitlines()[0])["text"] == "اردو ٹیسٹ ۱۲۳"
