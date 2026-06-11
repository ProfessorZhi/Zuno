import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from langchain.tools import tool
from loguru import logger

from agentchat.settings import app_settings


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
        return "当前没有可用的发件邮箱预设。请先到配置页添加邮箱槽位。"

    lines = ["当前可用的发件邮箱预设如下："]
    for account in accounts:
        lines.append(
            f"- 槽位名: {account['slot_name']} | 类型: {account['provider']} | 发件邮箱: {account['sender_email']} | 显示名: {account['display_name']}"
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

    available_slots = [str(account.get("slot_name", "")).strip() for account in accounts if str(account.get("slot_name", "")).strip()]
    if available_slots:
        raise ValueError("未找到匹配的发件箱槽位，可用槽位有: " + ", ".join(available_slots))

    raise ValueError("当前没有可用的发件邮箱预设。请先到配置页添加邮箱槽位。")


def _validate_account(account: dict[str, Any]) -> dict[str, Any]:
    sender_email = str(account.get("sender_email", "")).strip()
    auth_code = str(account.get("auth_code", "")).strip()
    smtp_host = str(account.get("smtp_host", "")).strip()
    smtp_port = int(account.get("smtp_port") or 465)
    use_ssl = bool(account.get("use_ssl", True))
    display_name = str(account.get("display_name", "")).strip() or sender_email

    if not sender_email:
        raise ValueError("发件邮箱预设缺少 sender_email。")
    if not auth_code:
        raise ValueError("发件邮箱预设缺少 auth_code。")
    if not smtp_host:
        raise ValueError("发件邮箱预设缺少 smtp_host。")

    return {
        "sender_email": sender_email,
        "auth_code": auth_code,
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "use_ssl": use_ssl,
        "display_name": display_name,
    }


@tool(parse_docstring=True)
def list_email_accounts() -> str:
    """
    查看当前系统里已经配置好的发件邮箱预设槽位。

    Returns:
        str: 可用的邮箱槽位列表，不包含授权码等敏感信息。
    """
    return _format_email_account_summaries()


@tool(parse_docstring=True)
def send_email(
    receiver: str,
    email_message: str,
    sender_slot: str = "",
    subject: str = "",
    sender: str = "",
    password: str = "",
):
    """
    向指定邮箱发送邮件，优先使用已配置好的发件邮箱槽位。

    Args:
        receiver (str): 收件人的邮箱地址。
        email_message (str): 邮件正文内容。
        sender_slot (str): 发件箱槽位名，例如 qq-main、qq-backup、office-main。优先推荐填写。
        subject (str): 邮件主题。不填时会使用默认主题。
        sender (str): 可选的发件邮箱地址，仅用于兼容旧调用。
        password (str): 可选的邮箱授权码，仅用于兼容旧调用。

    Returns:
        str: 邮件发送结果。
    """
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
    message["Subject"] = subject.strip() or "Zuno 为你发送了一封邮件"

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
        return f"邮件已发送，使用发件箱槽位: {sender_slot or account['sender_email']}"
    except Exception as err:
        logger.error(f"send email error: {err}")
        return f"发送邮件失败: {err}"
