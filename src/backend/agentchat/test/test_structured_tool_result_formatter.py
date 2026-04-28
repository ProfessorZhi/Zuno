from agentchat.services.structured_tool_result_formatter import (
    format_structured_tool_result,
)


def test_formats_market_ohlc_rows_with_deterministic_weekday_and_change():
    payload = {
        "data": [
            {
                "date": "2026-04-24T00:00:00+0000",
                "symbol": "NVDA",
                "open": 199.96,
                "high": 210.95,
                "low": 199.81,
                "close": 208.27,
                "volume": 213000000,
            },
            {
                "date": "2026-04-23T00:00:00+0000",
                "symbol": "NVDA",
                "open": 202.40,
                "high": 203.83,
                "low": 197.22,
                "close": 199.64,
                "volume": 109000000,
            },
        ]
    }

    formatted = format_structured_tool_result(payload)

    assert formatted is not None
    assert "结构化行情数据" in formatted
    assert "| 2026-04-24 | 周五 | NVDA | 199.96 | 210.95 | 199.81 | 208.27 | +8.63 | +4.32% | 213,000,000 |" in formatted
    assert "| 2026-04-23 | 周四 | NVDA | 202.40 | 203.83 | 197.22 | 199.64 |  |  | 109,000,000 |" in formatted
    assert "涨跌和涨跌幅由程序按相邻交易日收盘价计算" in formatted


def test_formats_market_ohlc_rows_from_python_repr_string():
    payload = (
        "{'data': ["
        "{'date': '2026-04-24T00:00:00+0000', 'symbol': 'NVDA', 'open': 199.96, "
        "'high': 210.95, 'low': 199.81, 'close': 208.27, 'volume': 213000000}, "
        "{'date': '2026-04-23T00:00:00+0000', 'symbol': 'NVDA', 'open': 202.40, "
        "'high': 203.83, 'low': 197.22, 'close': 199.64, 'volume': 109000000}"
        "]}"
    )

    formatted = format_structured_tool_result(payload)

    assert formatted is not None
    assert "| 2026-04-24 | 周五 | NVDA |" in formatted
    assert "+4.32%" in formatted
