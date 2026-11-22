# 환경 및 도구 확인 결과 (env_check)

## 1. 실행 환경
- OS: Linux (Ubuntu 24.04 x86_64)
- Python: 3.12.16
  - python-pptx: 1.0.2 설치 완료
- Node.js: v22.23.5
  - Playwright: 1.57.0 (Chromium headless 정상 구동 확인)

## 2. 기준 결과 재현 (`skill/reference/rx_afe/work/run_all.sh`)
- 실행 명령:
  ```bash
  export NODE_PATH=/home/antigravity/jmseo16/etf-dashboard/node_modules
  bash skill/reference/rx_afe/work/run_all.sh
  ```
- 실행 출력 요약:
  - 총 17개 뷰 렌더링 완료:
    `['b_top', 'b_slice', 'b_clk', 'u_top_term', 'u_top_tg', 'u_ctle', 'u_vga', 'u_summer', 'b_sa', 'u_sa_strongarm', 'b_sr', 'u_nand', 'u_inv', 'u_latch', 'b_dff', 'u_clk_term', 'u_clk_buf']`
  - HTML 생성 완료: `skill/reference/rx_afe/out/concept.html`
  - PPTX 생성 완료: `skill/reference/rx_afe/out/concept.pptx` (18 슬라이드)
  - 스크린샷 17장 생성 완료: `skill/reference/rx_afe/out/screenshots/*.png`
  - 검증기 실행 결과:
    - `summary`: `{'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}`
    - `self_test`: `{'injected': 57, 'caught': 57, 'all_caught': True}`
    - Auto checks: 29개 중 failing 0개

## 3. 판정
- 기준 결과 완벽 재현 성공 (화면 17, 연결 17, 품질 17 통과). 시험 진행 가능.
