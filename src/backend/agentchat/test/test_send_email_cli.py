from pathlib import Path

import yaml


def test_send_email_cli_lists_accounts(monkeypatch, capsys):
    from agentchat.tools.send_email import action as email_action
    from agentchat.tools.send_email import cli as email_cli

    monkeypatch.setattr(email_cli, "_load_runtime_settings", lambda: None)
    monkeypatch.setattr(email_action, "_format_email_account_summaries", lambda: "slot-a")

    exit_code = email_cli.main(["list-accounts"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "slot-a"


def test_send_email_cli_send_forwards_args(monkeypatch, capsys):
    from agentchat.tools.send_email import action as email_action
    from agentchat.tools.send_email import cli as email_cli

    recorded = {}

    def fake_send_email(**kwargs):
        recorded.update(kwargs)
        return "sent"

    monkeypatch.setattr(email_cli, "_load_runtime_settings", lambda: None)
    monkeypatch.setattr(email_action, "_send_email", fake_send_email)

    exit_code = email_cli.main(
        [
            "send",
            "--receiver",
            "receiver@example.com",
            "--message",
            "hello",
            "--sender-slot",
            "qq-main",
            "--subject",
            "notice",
            "--sender",
            "sender@example.com",
            "--password",
            "secret",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "sent"
    assert recorded == {
        "receiver": "receiver@example.com",
        "email_message": "hello",
        "sender_slot": "qq-main",
        "subject": "notice",
        "sender": "sender@example.com",
        "password": "secret",
    }


def test_send_email_manifest_declares_cli_tool():
    manifest_path = Path(__file__).resolve().parents[1] / "tools" / "send_email" / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["type"] == "cli"
    assert manifest["credentials"]["mode"] == "profiles"
    assert manifest["entry"]["module"] == "agentchat.tools.send_email.cli"
