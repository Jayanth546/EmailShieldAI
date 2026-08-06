from app.analyzers.attachment_analyzer import AttachmentAnalyzer


def test_safe_attachment():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "report.pdf",
        "photo.jpg",
    ])

    assert result["score"] == 0
    assert result["issues"] == []


def test_executable_attachment():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "invoice.exe",
    ])

    assert result["score"] == 30
    assert len(result["issues"]) == 1


def test_double_extension():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "invoice.pdf.exe",
    ])

    assert result["score"] == 55
    assert len(result["issues"]) == 2


def test_macro_document():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "salary.xlsm",
    ])

    assert result["score"] == 20
    assert len(result["issues"]) == 1


def test_archive():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "documents.zip",
    ])

    assert result["score"] == 10
    assert len(result["issues"]) == 1


def test_multiple_attachments():
    analyzer = AttachmentAnalyzer()

    result = analyzer.analyze([
        "invoice.pdf.exe",
        "salary.xlsm",
        "backup.zip",
    ])

    assert result["score"] == 85
    assert len(result["issues"]) == 4
