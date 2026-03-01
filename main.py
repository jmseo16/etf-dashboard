"""
ETF 대시보드 - 노션 자동 업데이트
매일 KST 07:00 실행 (GitHub Actions)
"""

from datetime import datetime
import utils.notion as notion
import utils.catbox as catbox
import utils.font as font

# ── 차트 모듈 import (완성된 것만 추가) ──
from charts import sector_etf
# from charts import style_etf      # 추후 추가
# from charts import fear_greed     # 추후 추가
# from charts import economic       # 추후 추가
# from charts import sp500_pe       # 추후 추가
# from charts import m2             # 추후 추가
# from charts import nya200r        # 추후 추가
# from charts import qqqm           # 추후 추가

CHARTS = [
    sector_etf,
    # style_etf,
    # fear_greed,
    # economic,
    # sp500_pe,
    # m2,
    # nya200r,
    # qqqm,
]

TODAY = datetime.now().strftime("%Y.%m.%d")

def run():
    print(f"\n🚀 ETF 대시보드 업데이트 시작 [{TODAY}]")
    print("=" * 50)

    # 한글 폰트 초기화
    font.setup()

    # 노션 페이지 초기화
    print("🗑️  기존 블록 삭제 중...")
    notion.delete_all_blocks()
    notion.update_title(f"📊 ETF 대시보드 | {TODAY} 업데이트")

    # 각 차트 순서대로 실행
    results = []
    for chart in CHARTS:
        name = chart.__name__.split(".")[-1]
        print(f"\n📈 [{name}] 시작...")
        try:
            data    = chart.fetch()           # 1. 데이터 수집
            img     = chart.draw(data)        # 2. 차트 생성
            url     = catbox.upload(img)      # 3. 이미지 업로드
            blocks  = chart.make_blocks(data, url)  # 4. 노션 블록 생성
            notion.append_blocks(blocks)      # 5. 노션에 삽입
            print(f"✅ [{name}] 완료")
            results.append((name, "✅"))
        except Exception as e:
            print(f"❌ [{name}] 실패: {e}")
            results.append((name, f"❌ {e}"))
            continue  # 하나 실패해도 다음 차트 계속 실행

    # 최종 결과 요약
    print(f"\n{'='*50}")
    print("📋 실행 결과 요약")
    for name, status in results:
        print(f"  {status}  {name}")
    print("=" * 50)

if __name__ == "__main__":
    run()
