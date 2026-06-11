import ast
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


_WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
_OHLC_FIELDS = {"date", "open", "high", "low", "close"}


@dataclass(frozen=True)
class MarketRow:
    trade_date: date
    symbol: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None


def format_structured_tool_result(payload: Any) -> str | None:
    normalized = _coerce_payload(payload)
    rows = _extract_market_rows(normalized)
    if not rows:
        return None

    rows_by_date = sorted(rows, key=lambda item: item.trade_date)
    previous_close_by_date = {
        current.trade_date: previous.close
        for previous, current in zip(rows_by_date, rows_by_date[1:])
    }

    lines = [
        "结构化行情数据（由程序确定性整理，模型不要重新计算日期或涨跌幅）：",
        "",
        "| 日期 | 星期 | 股票代码 | 开盘 | 最高 | 最低 | 收盘 | 涨跌 | 涨跌幅 | 成交量 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(rows, key=lambda item: item.trade_date, reverse=True):
        previous_close = previous_close_by_date.get(row.trade_date)
        change = row.close - previous_close if previous_close is not None else None
        change_pct = (change / previous_close * Decimal("100")) if change is not None and previous_close else None
        lines.append(
            "| "
            + " | ".join(
                [
                    row.trade_date.isoformat(),
                    _WEEKDAYS[row.trade_date.weekday()],
                    row.symbol,
                    _format_money(row.open),
                    _format_money(row.high),
                    _format_money(row.low),
                    _format_money(row.close),
                    _format_signed_money(change),
                    _format_signed_percent(change_pct),
                    _format_volume(row.volume),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "说明：涨跌和涨跌幅由程序按相邻交易日收盘价计算；缺少上一交易日时留空，不要编造。",
        ]
    )
    return "\n".join(lines)


def _coerce_payload(payload: Any) -> Any:
    if not isinstance(payload, str):
        return payload
    text = payload.strip()
    if not text:
        return payload
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return payload


def _extract_market_rows(payload: Any) -> list[MarketRow]:
    candidates = _find_lists(payload)
    for candidate in candidates:
        rows = [_coerce_market_row(item) for item in candidate if isinstance(item, dict)]
        rows = [row for row in rows if row is not None]
        if rows:
            return rows
    if isinstance(payload, dict):
        row = _coerce_market_row(payload)
        return [row] if row else []
    return []


def _find_lists(payload: Any) -> list[list[Any]]:
    if isinstance(payload, list):
        return [payload]
    if not isinstance(payload, dict):
        return []

    lists: list[list[Any]] = []
    for key in ("data", "results", "items", "values"):
        value = payload.get(key)
        if isinstance(value, list):
            lists.append(value)
    for value in payload.values():
        if isinstance(value, dict):
            lists.extend(_find_lists(value))
    return lists


def _coerce_market_row(item: dict[str, Any]) -> MarketRow | None:
    lowered = {str(key).lower(): value for key, value in item.items()}
    if not _OHLC_FIELDS.issubset(lowered):
        return None

    trade_date = _parse_date(lowered.get("date"))
    if trade_date is None:
        return None
    try:
        return MarketRow(
            trade_date=trade_date,
            symbol=str(lowered.get("symbol") or lowered.get("ticker") or "").strip() or "-",
            open=_to_decimal(lowered["open"]),
            high=_to_decimal(lowered["high"]),
            low=_to_decimal(lowered["low"]),
            close=_to_decimal(lowered["close"]),
            volume=_to_decimal(lowered["volume"]) if lowered.get("volume") is not None else None,
        )
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    date_part = value.strip()[:10]
    try:
        return date.fromisoformat(date_part)
    except ValueError:
        return None


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _format_money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _format_signed_money(value: Decimal | None) -> str:
    if value is None:
        return ""
    amount = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{amount:+.2f}"


def _format_signed_percent(value: Decimal | None) -> str:
    if value is None:
        return ""
    amount = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{amount:+.2f}%"


def _format_volume(value: Decimal | None) -> str:
    if value is None:
        return ""
    return f"{int(value):,}"
