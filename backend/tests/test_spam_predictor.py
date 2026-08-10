from ml.prediction.spam_predictor import SpamPredictor


def test_spam_predictor_loads():
    predictor = SpamPredictor()

    assert predictor.model is not None


def test_default_threshold():
    predictor = SpamPredictor()

    assert predictor.threshold == 0.50


def test_custom_threshold():
    predictor = SpamPredictor(threshold=0.70)

    assert predictor.threshold == 0.70


def test_invalid_threshold_below_zero():
    try:
        SpamPredictor(threshold=-0.1)
        assert False
    except ValueError:
        pass


def test_invalid_threshold_above_one():
    try:
        SpamPredictor(threshold=1.1)
        assert False
    except ValueError:
        pass


def test_spam_email_prediction():
    predictor = SpamPredictor()

    result = predictor.predict(
        "Congratulations! You won $5000. Click here immediately."
    )

    assert result["label"] == "spam"
    assert 0.0 <= result["spam_probability"] <= 1.0
    assert 0.0 <= result["ham_probability"] <= 1.0


def test_normal_email_prediction():
    predictor = SpamPredictor()

    result = predictor.predict(
        "Hello John, thank you for your email. Regards, Alice."
    )

    assert result["label"] == "ham"
    assert 0.0 <= result["spam_probability"] <= 1.0
    assert 0.0 <= result["ham_probability"] <= 1.0


def test_empty_email_prediction():
    predictor = SpamPredictor()

    result = predictor.predict("")

    assert result["label"] == "ham"
    assert result["spam_probability"] == 0.0
    assert result["ham_probability"] == 1.0


def test_non_string_email_raises_type_error():
    predictor = SpamPredictor()

    try:
        predictor.predict(None)
        assert False
    except TypeError:
        pass
