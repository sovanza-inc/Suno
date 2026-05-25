from suno.evaluation.metrics import cer, normalize_urdu, wer


def test_identical():
    refs = ["پاکستان زندہ باد"]
    hyps = ["پاکستان زندہ باد"]
    assert wer(refs, hyps) == 0.0
    assert cer(refs, hyps) == 0.0


def test_normalize_strips_punctuation():
    raw = "اردو، ٹیسٹ! یہ ہے۔"
    norm = normalize_urdu(raw)
    assert "،" not in norm
    assert "۔" not in norm
    assert "!" not in norm


def test_normalize_preserves_code_switching():
    raw = "Hello، یہ test ہے"
    norm = normalize_urdu(raw)
    assert "Hello" in norm
    assert "test" in norm


def test_normalize_preserves_numerals():
    raw = "میں نے 5 سیب کھائے"
    norm = normalize_urdu(raw)
    assert "5" in norm


def test_wer_one_substitution():
    refs = ["a b c d e"]
    hyps = ["a b X d e"]
    # 1 substitution out of 5 words -> 0.2
    assert abs(wer(refs, hyps, normalize=False) - 0.2) < 1e-9
