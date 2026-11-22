# 분류 검토 보고서 — rx_l1 (rxbyte_top)
> **검토 주체 공지**: 같은 모델이 검토함 (GLM-4 분류 역할 및 Claude 분류 검토 역할을 단일 모델이 수행함)

## 1. 검토 요약
- 검토 대상: `runs/rx_l1/glm/out/` (`classification.md`, `annotations.json`, `block_dictionary.json`)
- 검토 근거: `spec/DRAWING_PLAN.md` §2.3–2.7
- 판정: **PASS (수정 권고 0건, 분류 및 사전 대응 타당)**

## 2. 세부 검토 항목
1. **고속 데이터 입력 및 클럭 입력 판정 (§2.4)**:
   - `dq<7:0>`: 8비트 DDR DQ 데이터 패드 입력으로, 각 레인의 `dqslice`에 직결되므로 고속 데이터 입력 판정 타당.
   - `dqs_t, dqs_c`: 차동 DQS 데이터 스트로브 입력으로, `dqsrx` 차동 증폭기 및 `dqsgate` 게이팅 블록을 거쳐 8개 DQ 슬라이스의 센스앰프 클럭 트리로 분배되므로 고속 클럭 입력 판정 타당.
   - `qr<7:0>`, `qf<7:0>`: 상승 에지 및 하강 에지에서 래치된 8비트 복구 데이터 출력으로 고속 데이터 출력 판정 타당.
   - `wl_out`: Write Leveling 위상 판정 결과 출력으로 중요 제어 출력 판정 타당.

2. **제어 분류 및 K# 끝점 판정 (§2.5)**:
   - `vrc<5:0>`: 64레벨 R-ladder VREF DAC의 디지털 제어 코드로 K1(기준 전압 코드, 버스) 판정 정확.
   - `t1w<2:0>`, `t2w<1:0>`: `sadfe`의 탭 1 및 탭 2 DFE 가중치 계수 코드로 K1(DFE 가중치, 버스) 판정 정확.
   - `ddl<2:0>`: DQS 수신 경로 디지털 딜레이 라인 튜닝 코드로 K1(지연 제어, 버스) 판정 정확.
   - `odt_en`, `rtt<2:0>`: DQS 및 DQ 입력 패드의 온다이 저항 종단 제어로 K4(종단 제어, 버스 및 실선) 판정 정확.
   - `rx_en`: 수신기 전체 전력 및 동작 제어로 K3(켜기, 1비트 실선) 판정 정확.
   - `gate_open`: DQS 게이팅 윈도우 인에이블 신호로 K2(선택, 1비트 실선) 판정 정확.
   - `wl_en`, `wl_ck`: Write Leveling 검출기 인에이블 및 기준 클럭으로 K2/K3 판정 정확.
   - `slp`: 파워다운 슬립 스위치 제어로 K3 판정 정확.
   - `ibias`: 아날로그 전류 바이어스로 K7(바이어스, 숨김) 판정 정확.
   - `vdd, vddq, vss, vssq`: 전원 및 접지 레일로 전원(숨김) 판정 정확.

3. **사전 대응 (§2.6)**:
   - `padesd`: 입력 보호 ESD 소자 -> `termination_esd` (입력선 위 표시)
   - `odtleg3`: 3단계 선택 ODT 저항 레그 -> `termination` (입력선 위 가변 R 표시)
   - `odtctl`: ODT 제어 디코더 -> DEC 박스
   - `biasgen`: 바이어스 전압 생성기 -> `bias` (박스)
   - `vrefdac`: 64단계 저항 사다리 DAC -> `dac` (VREF DAC 박스)
   - `dqsamp`: CML 차동 버퍼 -> `cml_buffer` (삼각형 BUF)
   - `acamp`: AC 결합 증폭기 -> `amplifier` (삼각형 AMP)
   - `dqsrx`: DQS 차동 수신기 복합 블록 -> `composite` (박스)
   - `dqsgate`: DQS 게이팅 제어 블록 -> `composite` (박스)
   - `dly3`: 3비트 제어 딜레이 라인 -> `delay_line` (DLY 박스)
   - `sbamp`: 단일-차동 변환 프리앰프 -> `vga` (삼각형 VGA)
   - `sadfe`: StrongArm 2-탭 DFE -> `strongarm` (삼각형 + 클럭)
   - `srnand`: SR 래치 -> `sr_latch` (SR 래치 박스)
   - `dqslice`: DQ 레인 수신 슬라이스 -> `composite` (박스)
   - `wldet`: Write Leveling 검출기 -> `phase_detector` (WL DET 박스)
   - `rxbyte_top`: 최상위 바이트 수신기 -> `composite` (박스)

4. **판정**:
   - 수정 권고 없음. GLM 초안 확정.
