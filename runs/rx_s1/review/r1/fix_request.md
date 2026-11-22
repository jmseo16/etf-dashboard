# 수정 요청 — rx_s1 회차 1  (이 목록은 최소 범위다. 같은 규칙을 전체에 적용하고 바뀐 화면을 `scene_sha`로 보고하라)

*(같은 모델이 검토한 목록이다.)* 근거는 netlist 줄과 명세서 조항만 적는다.

- **F1 (M11, 그린 쪽)** 주석·제목에 쓴 질문 번호가 `classification.md` 의 질문 번호와 다르다. `u_rx_pre` 주석 "질문 Q7", `u_top_lpf` 주석 "질문 Q6" → 실제 번호는 Q4 (D=S 묶인 MOS 커패시터). 모든 화면의 주석에서 질문 번호를 `annotations.json` 의 id 와 대조해 고친다. 근거: §3.5-7 (설명 문구가 틀리면 불합격).
- **F2 (M3·J1, 그린 쪽)** `vref`, `net3`(기준 전압)는 §2.5-4 표 "기준" 행: 회색 실선 + 이름표, 받는 블록의 둘째 입력 핀. b_top 에서 vref 포트→LPF→AMP.vref 선을 회색으로 그린다(선 굵기·실선은 그대로). 사이드 패널 분류 요약에 "기준 입력: vref" 줄을 더하고, b_top 설명(주석)에 "vref — 기준 전압 (RC 필터 뒤 AMP 둘째 입력)"을 적는다. 근거: netlist `r0 vref net3 5k`, `xi24 … net3 …`, 명세서 §2.5-4, §2.5-6.
- **F3 (J2, 그린 쪽)** 개념 기호로 묶은 소자의 범례를 화면 아래에 그린다 ("묶음·병합 (bundles / merged)", SKILL §6.5, 명세서 §3.4-3): `u_dfe_sum` X_DAC<3:0> = mn10..mn17, `u_sa_dt_stage1` C_OF_N = mn7+mn8 ∥ mn9+mn10, C_OF_P = mn11+mn12 ∥ mn13+mn14, MOS 커패시터를 C 기호로 그린 `u_rx_pre`(mn8, mn9), `u_top_lpf`(mn0). 크기는 netlist 에서 읽어 전부 나열(예: `W 400n L 30n m 8,4,2,1`). 지금은 사이드 패널 주석에만 있다.
- **F4 (J4★, 그린 쪽 + 명세서)** (a) `u_dfe_sum`: 주 쌍 · 귀환 쌍 · 부호 스위치 4개를 축 대칭(거울상)으로 다시 배치한다. 지금은 부호 스위치와 귀환 쌍이 한쪽에 몰려 있고 outp/outn 이 이름표다. 근거: §3.3-1, §3.3-2. (b) `u_sa_dt_stage2` 의 교차 결합 인버터 쌍(mp3/mn3 ↔ mp4/mn4, netlist `mp3 outp outn net64`, `mn3 outp outn vss`, `mp4 outn outp net64`, `mn4 outn outp vss`)을 §3.3-7 처럼 90° 돌려 그린다 — 단 도구에 회전된 MOS 기호가 없고 명세서 §3.4 기호 표에도 회전 MOS 모양이 없다. 못 하면 못 한 이유를 적는다.

바뀌어도 되는 화면: b_top(F2), u_rx_pre·u_top_lpf(F1·F3), u_dfe_sum(F3·F4), u_sa_dt_stage1(F3), u_sa_dt_stage2(F4). 그 밖의 화면은 `scene_sha` 가 같아야 한다.
