from ml.prediction.spam_predictor import SpamPredictor


def test_spam_predictor_loads():
    predictor = SpamPredictor()

    assert predictor.model is not None


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
