# 환경 확인 (회차 0 전)
- 복원: restore.py 실행, 34 files restored, 0 checksum mismatches.
- 도구: Python 3.13.18, python-pptx 1.0.2, Node v22.23.4, Playwright(node 1.63, python 1.65) + chromium headless shell (pip install playwright; python3 -m playwright install chromium 로 설치). 실행 시 NODE_PATH=/opt/node22/lib/node_modules:/opt/node-tools/node_modules 필요.
- `bash skill/reference/rx_afe/work/run_all.sh` 실행 결과(약 12초, 오류 종료 없음):
  - verify_report.json summary = {'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}
  - self_checklist.json self_test = 위 출력 참조(아래 줄)
  - classification.md / annotations.json / verify_report.json / block_dictionary.json 을 expected/ 와 cmp 한 결과는 아래.
- LibreOffice(PPTX→PNG 변환)는 확인하지 않음.
  - self_test = {'injected': 57, 'caught': 57, 'all_caught': True}; 네 파일 모두 expected/와 바이트 동일(cmp). 기준 결과 재현 성공.
