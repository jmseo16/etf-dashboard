이 목록은 최소 범위다. 같은 규칙을 전체에 적용하고 바뀐 화면을 `scene_sha`로 보고하라.

# 회차 1 수정 요청 목록 (rx_s1)
검토 주체: Claude 역할 대행 (같은 모델이 검토함)

## 1. M8 (출력별 극성 및 동그라미)
- 근거: DRAWING_PLAN §4.1-13, §3.4-6, V19
- 대상: `b_top` 내 `xi22` (ODT 디코더 인버터 출력 enb<2:0>)
- 내용: netlist 상 인버터 논리 출력이므로 버블(반전 동그라미) 표기 준수 필요.

## 2. M13 (핀 방향 V18 표 준수)
- 근거: DRAWING_PLAN V24, V18, §3.2
- 대상:
  - `xi20.pad`, `xi21.pad`: PAD 연결 방향 검토
  - `xi22.odt_en`, `xi22.rtt<2:0>`: 입력 핀 배치 방향 검토
  - `xi24.sel_m`, `xi24.sel_l`: 선택 제어 핀 상단/좌측 배치 규격 일치화

## 3. M5 및 M4 (품질 검사 개선)
- 근거: DRAWING_PLAN §4.1-5, §1.4-9
- 내용: `b_top`의 텍스트 겹침(text_overlap), 짧은 꺾임(short_jogs), 블록 간 교차선(avoidable_crossings) 최소화.
