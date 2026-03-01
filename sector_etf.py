"""
섹터별(ETF) 현황 차트
- 데이터: Yahoo Finance (yfinance)
- 기간: 최근 한달
"""

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from datetime import datetime, timedelta
import utils.notion as notion

# ── 상수 ──────────────────────────────────────────
ETFS = {
    "XLE":  ("에너지",      "Energy Select Sector SPDR Fund",               "석유, 가스, 에너지 기업. ExxonMobil, Chevron 등. 유가와 높은 연관성."),
    "XLU":  ("유틸리티",    "Utilities Select Sector SPDR Fund",             "전기, 가스, 수도 공급 기업. 경기 방어적. 금리 민감도 높음."),
    "XLP":  ("필수소비재",  "Consumer Staples Select Sector SPDR Fund",      "음식, 음료, 생활용품. P&G, Coca-Cola 등. 경기침체에 강함."),
    "XLI":  ("산업",        "Industrial Select Sector SPDR Fund",            "항공, 방산, 기계, 물류 기업. 경기 민감 섹터."),
    "XLB":  ("소재",        "Materials Select Sector SPDR Fund",             "화학, 광업, 포장재 기업. 원자재 가격과 연동."),
    "XLRE": ("부동산",      "Real Estate Select Sector SPDR Fund",           "리츠(REIT) 중심. 금리 하락 시 수혜."),
    "XLC":  ("통신",        "Communication Services Select Sector SPDR Fund","Meta, Alphabet, Netflix 등. 통신 + 미디어 혼합."),
    "XLF":  ("금융",        "Financial Select Sector SPDR Fund",             "은행, 보험, 증권사. 금리 상승 수혜 섹터."),
    "XLY":  ("임의소비재",  "Consumer Discretionary Select Sector SPDR Fund","Amazon, Tesla 등. 경기 좋을 때 강세."),
    "XLK":  ("기술",        "Technology Select Sector SPDR Fund",            "Apple, Microsoft, Nvidia 등. 성장주 중심."),
}

COLORS = ["#e74c3c","#3498db","#2ecc71","#f39c12","#9b59b6",
          "#1abc9c","#e67e22","#34495e","#e91e63","#00bcd4"]

TODAY = datetime.now().strftime("%Y.%m.%d")
IMG_PATH = "/tmp/sector_etf.png"

# ── 1. 데이터 수집 ─────────────────────────────────
def fetch() -> dict:
    end   = datetime.today()
    start = end - timedelta(days=35)
    raw   = yf.download(list(ETFS.keys()), start=start, end=end,
                        auto_adjust=True, progress=False)
    data  = raw["Close"]
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(1)
    data = data.dropna(axis=1, how="all")

    returns      = (data / data.iloc[0] - 1) * 100
    final_ret    = returns.iloc[-1].sort_values(ascending=False)
    latest       = data.iloc[-1]
    day_change   = (data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100

    return {
        "data": data,
        "returns": returns,
        "final_ret": final_ret,
        "latest": latest,
        "day_change": day_change,
    }

# ── 2. 차트 생성 ───────────────────────────────────
def draw(d: dict) -> str:
    returns, final_ret = d["returns"], d["final_ret"]

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    for i, ticker in enumerate(final_ret.index):
        color = COLORS[i % len(COLORS)]
        ax.plot(returns.index, returns[ticker],
                linewidth=1.8, color=color, alpha=0.9)
        ax.annotate(f"{ticker} {final_ret[ticker]:+.1f}%",
                    xy=(returns.index[-1], returns[ticker].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points",
                    fontsize=8.5, color=color, va="center")

    best, worst = final_ret.index[0], final_ret.index[-1]
    ax.text(0.02, 0.97, f"▲ {ETFS[best][0]} {final_ret[best]:+.1f}%",
            transform=ax.transAxes, fontsize=14, color="#ff6b6b",
            fontweight="bold", va="top")
    ax.text(0.02, 0.05, f"▼ {ETFS[worst][0]} {final_ret[worst]:+.1f}%",
            transform=ax.transAxes, fontsize=14, color="#74b9ff",
            fontweight="bold")

    ax.axhline(0, color="white", linewidth=0.8, linestyle="--", alpha=0.4)
    ax.set_title(f"섹터별(ETF) 현황  |  {TODAY} 기준",
                 fontsize=18, color="white", fontweight="bold", pad=15)
    ax.set_ylabel("수익률 (%)", color="white", fontsize=11)
    ax.tick_params(colors="white", labelsize=9)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")
    ax.grid(axis="y", color="#333", linewidth=0.5, alpha=0.5)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m/%d"))
    plt.xticks(rotation=30, color="white")
    ax.set_xlim(right=returns.index[-1] + timedelta(days=4))
    fig.text(0.99, 0.01, "출처: Yahoo Finance, 기간: 최근 한달",
             ha="right", fontsize=8, color="#aaa")

    plt.tight_layout()
    plt.savefig(IMG_PATH, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    return IMG_PATH

# ── 3. 노션 블록 생성 ──────────────────────────────
def make_blocks(d: dict, img_url: str) -> list:
    final_ret  = d["final_ret"]
    latest     = d["latest"]
    day_change = d["day_change"]

    def pct_color(v):
        return "red" if v < 0 else "green"

    blocks = [
        notion.heading("📈 섹터별 수익률 차트"),
        notion.callout(f"🗓️ 업데이트: {TODAY}  |  기간: 최근 한달  |  출처: Yahoo Finance"),
        notion.image_block(img_url),
        notion.divider(),
        notion.heading("📋 티커별 현황 & 설명"),
    ]

    # 티커별 테이블
    header = ["티커", "섹터", "현재가", "일간변동", "월간수익률", "설명"]
    rows = []
    for ticker in final_ret.index:
        kr, _, desc = ETFS.get(ticker, ("", "", ""))
        rows.append([
            ticker,
            kr,
            f"${latest.get(ticker, 0):.2f}",
            (f"{day_change.get(ticker, 0):+.2f}%", pct_color(day_change.get(ticker, 0))),
            (f"{final_ret[ticker]:+.2f}%",          pct_color(final_ret[ticker])),
            desc,
        ])
    blocks.append(_make_table(header, rows))
    blocks.append(notion.divider())

    # Raw 테이블
    blocks.append(notion.heading("🗃️ Raw Data"))
    raw_header = ["항목"] + list(final_ret.index)
    raw_rows = [
        ["현재가($)"]   + [f"${latest.get(t, 0):.2f}"            for t in final_ret.index],
        ["일간변동(%)"] + [f"{day_change.get(t, 0):+.2f}%"       for t in final_ret.index],
        ["월간수익(%)"] + [f"{final_ret[t]:+.2f}%"               for t in final_ret.index],
    ]
    blocks.append(_make_table(raw_header, raw_rows, has_col_header=False, has_row_header=True))

    return blocks

# ── 헬퍼: 테이블 블록 생성 ────────────────────────
def _make_table(header, rows, has_col_header=True, has_row_header=False):
    def cell(val):
        """문자열 또는 (문자열, 색상) 튜플 처리"""
        if isinstance(val, tuple):
            text, color = val
            return [{"type": "text", "text": {"content": text},
                     "annotations": {"bold": True, "color": color}}]
        return [{"type": "text", "text": {"content": str(val)}}]

    table_rows = []
    # 헤더 행
    table_rows.append({
        "object": "block", "type": "table_row",
        "table_row": {"cells": [
            [{"type": "text", "text": {"content": h},
              "annotations": {"bold": True}}] for h in header
        ]}
    })
    # 데이터 행
    for row in rows:
        table_rows.append({
            "object": "block", "type": "table_row",
            "table_row": {"cells": [cell(v) for v in row]}
        })

    return {
        "object": "block", "type": "table",
        "table": {
            "table_width": len(header),
            "has_column_header": has_col_header,
            "has_row_header": has_row_header,
            "children": table_rows,
        }
    }
