import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from langchain.tools import tool
from loguru import logger

from zuno.settings import app_settings


def _normalize_email_accounts() -> list[dict[str, Any]]:
    tools = getattr(app_settings, "tools", None)
    if tools is None:
        return []

    email_config = getattr(tools, "email", None)
    if isinstance(email_config, dict):
        accounts = email_config.get("accounts") or []
        if isinstance(accounts, list):
            return [item for item in accounts if isinstance(item, dict)]

    return []


def _list_email_account_summaries() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for account in _normalize_email_accounts():
        slot_name = str(account.get("slot_name", "")).strip()
        sender_email = str(account.get("sender_email", "")).strip()
        if not slot_name or not sender_email:
            continue
        summaries.append(
            {
                "slot_name": slot_name,
                "provider": str(account.get("provider", "custom")).strip() or "custom",
                "sender_email": sender_email,
                "display_name": str(account.get("display_name", "")).strip() or sender_email,
                "smtp_host": str(account.get("smtp_host", "")).strip(),
                "smtp_port": int(account.get("smtp_port") or 465),
                "use_ssl": bool(account.get("use_ssl", True)),
            }
        )
    return summaries


def _format_email_account_summaries() -> str:
    accounts = _list_email_account_summaries()
    if not accounts:
        return "褰撳墠娌℃湁鍙敤鐨勫彂浠堕偖绠遍璁俱€傝鍏堝埌閰嶇疆椤垫坊鍔犻偖绠辨Ы浣嶃€?"

    lines = ["褰撳墠鍙敤鐨勫彂浠堕偖绠遍璁惧涓嬶細"]
    for account in accounts:
        lines.append(
            f"- 妲戒綅鍚? {account['slot_name']} | 绫诲瀷: {account['provider']} | 鍙戜欢閭: {account['sender_email']} | 鏄剧ず鍚? {account['display_name']}"
        )
    return "\n".join(lines)


def _resolve_email_account(sender_slot: str, sender: str, password: str) -> dict[str, Any]:
    accounts = _normalize_email_accounts()
    normalized_slot = sender_slot.strip().lower()
    normalized_sender = sender.strip().lower()

    if normalized_slot:
        for account in accounts:
            slot_name = str(account.get("slot_name", "")).strip().lower()
            if slot_name == normalized_slot:
                return account

    if normalized_sender:
        for account in accounts:
            sender_email = str(account.get("sender_email", "")).strip().lower()
            if sender_email == normalized_sender:
                return account

    if sender.strip() and password.strip():
        return {
            "slot_name": sender_slot.strip() or sender.strip(),
            "provider": "custom",
            "sender_email": sender.strip(),
            "auth_code": password.strip(),
            "smtp_host": "",
            "smtp_port": 465,
            "use_ssl": True,
            "display_name": sender.strip(),
        }

    available_slots = [
        str(account.get("slot_name", "")).strip()
        for account in accounts
        if str(account.get("slot_name", "")).strip()
    ]
    if available_slots:
        raise ValueError("鏈壘鍒板尮閰嶇殑鍙戜欢绠辨Ы浣嶏紝鍙敤妲戒綅鏈? " + ", ".join(available_slots))

    raise ValueError("褰撳墠娌℃湁鍙敤鐨勫彂浠堕偖绠遍璁俱€傝鍏堝埌閰嶇疆椤垫坊鍔犻偖绠辨Ы浣嶃€?")


def _validate_account(account: dict[str, Any]) -> dict[str, Any]:
    sender_email = str(account.get("sender_email", "")).strip()
    auth_code = str(account.get("auth_code", "")).strip()
    smtp_host = str(account.get("smtp_host", "")).strip()
    smtp_port = int(account.get("smtp_port") or 465)
    use_ssl = bool(account.get("use_ssl", True))
    display_name = str(account.get("display_name", "")).strip() or sender_email

    if not sender_email:
        raise ValueError("鍙戜欢閭棰勮缂哄皯 sender_email銆?")
    if not auth_code:
        raise ValueError("鍙戜欢閭棰勮缂哄皯 auth_code銆?")
    if not smtp_host:
        raise ValueError("鍙戜欢閭棰勮缂哄皯 smtp_host銆?")

    return {
        "sender_email": sender_email,
        "auth_code": auth_code,
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "use_ssl": use_ssl,
        "display_name": display_name,
    }


@tool
def list_email_accounts() -> str:
    """List configured email sender slots."""
    return _format_email_account_summaries()


@tool
def send_email(
    receiver: str,
    email_message: str,
    sender_slot: str = "",
    subject: str = "",
    sender: str = "",
    password: str = "",
):
    """Send an email using a configured sender slot or explicit SMTP credentials."""
    return _send_email(
        receiver=receiver,
        email_message=email_message,
        sender_slot=sender_slot,
        subject=subject,
        sender=sender,
        password=password,
    )


def _send_email(
    receiver: str,
    email_message: str,
    sender_slot: str = "",
    subject: str = "",
    sender: str = "",
    password: str = "",
):
    account = _validate_account(_resolve_email_account(sender_slot, sender, password))

    message = MIMEMultipart()
    message["From"] = Header(f"{account['display_name']} <{account['sender_email']}>")
    message["To"] = receiver
    message["Subject"] = subject.strip() or "Zuno 涓轰綘鍙戦€佷簡涓€灏侀偖浠?"

    try:
        message.attach(MIMEText(email_message, "plain", "utf-8"))

        if account["use_ssl"]:
            server = smtplib.SMTP_SSL(account["smtp_host"], account["smtp_port"])
        else:
            server = smtplib.SMTP(account["smtp_host"], account["smtp_port"])
            server.starttls()

        server.login(account["sender_email"], account["auth_code"])
        server.sendmail(account["sender_email"], receiver, message.as_string())
        server.quit()

        logger.info(
            "send_email sender_slot={}, sender={}, receiver={}",
            sender_slot or account["sender_email"],
            account["sender_email"],
            receiver,
        )
        return f"閭欢宸插彂閫侊紝浣跨敤鍙戜欢绠辨Ы浣? {sender_slot or account['sender_email']}"
    except Exception as err:
        logger.error(f"send email error: {err}")
        return f"鍙戦€侀偖浠跺け璐? {err}"
