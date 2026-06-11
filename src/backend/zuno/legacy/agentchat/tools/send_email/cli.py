import argparse
import asyncio
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from agentchat.settings import initialize_app_settings, resolve_app_config_path
from agentchat.tools.send_email import action as email_action


def _resolve_runtime_config_path() -> Path | None:
    path = resolve_app_config_path()
    return path if path.exists() else None


def _load_runtime_settings() -> Path | None:
    config_path = _resolve_runtime_config_path()
    if config_path is not None:
        asyncio.run(initialize_app_settings(str(config_path)))
    return config_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="send-email",
        description="Send email via configured sender slots or explicit SMTP credentials.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "list-accounts",
        help="List configured email sender slots.",
    )

    send_parser = subparsers.add_parser(
        "send",
        help="Send an email.",
    )
    send_parser.add_argument("--receiver", required=True, help="Receiver email address.")
    send_parser.add_argument("--message", required=True, help="Plain-text email body.")
    send_parser.add_argument("--sender-slot", default="", help="Configured sender slot name.")
    send_parser.add_argument("--subject", default="", help="Email subject.")
    send_parser.add_argument("--sender", default="", help="Explicit sender email for fallback mode.")
    send_parser.add_argument("--password", default="", help="Explicit auth code for fallback mode.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    _load_runtime_settings()

    if args.command == "list-accounts":
        print(email_action._format_email_account_summaries())
        return 0

    result = email_action._send_email(
        receiver=args.receiver,
        email_message=args.message,
        sender_slot=args.sender_slot,
        subject=args.subject,
        sender=args.sender,
        password=args.password,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
