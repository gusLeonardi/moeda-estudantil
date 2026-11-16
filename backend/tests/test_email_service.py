from email.message import EmailMessage

from app.services import email_service


def test_smtp_message_encodes_subject_and_html_as_utf8(monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def starttls(self, **kwargs): pass
        def login(self, *args): pass
        def send_message(self, message): captured["message"] = message

    monkeypatch.setenv("SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "mailer@example.test")
    monkeypatch.setenv("SMTP_PASSWORD", "test-only")
    monkeypatch.setenv("SMTP_FROM", "mailer@example.test")
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    assert email_service.enviar_email("user@example.test", "Ativação de conta", "<p>Token temporário</p>")
    message: EmailMessage = captured["message"]
    assert message["Subject"] == "Ativação de conta"
    parts = list(message.iter_parts())
    assert all(part.get_content_charset() == "utf-8" for part in parts)
    assert "Token temporário" in parts[1].get_content()
