# rx_l1 — 회차 0 (분류)
> **검토 주체 공지**: 같은 모델이 검토함 (GLM-4 분류 역할 및 Claude 분류 검토 역할을 단일 모델이 수행함)

## 요약
- 상태: 끝남
- 한 일:
  - rx_l1(rxbyte_top) 넷리스트 정밀 분석 및 신호/블록 분류 초안 생성
  - 8개 DQ 데이터 라인, 차동 DQS 스트로브, 바이트 복구 출력 및 DFE/VREF/ODT 제어 버스 전수 식별
  - Claude 관점의 분류 검토 완료 및 r0_a_classify, r0_c_review 스냅샷 생성
- 못 한 일과 이유:
  - 없음 (분류 및 검토 완료)

## 분류 (회차 0에서 채우고, 바뀌면 다시 적는다)
- 고속 데이터 입력: dq7, dq6, dq5, dq4, dq3, dq2, dq1, dq0 / 고속 클럭 입력: dqs_t, dqs_c / 고속 출력: qr<7:0>, qf<7:0>, wl_out
- 그리는 제어 (이름, K#, 끝점 핀):
  - vrc<5:0> (K1, xi2.vrc<5:0>)
  - t1w<2:0> (K1, xi30..xi37.w1<2:0>)
  - t2w<1:0> (K1, xi30..xi37.w2<1:0>)
  - ddl<2:0> (K1, xi10/xi11.ddl<2:0>)
  - odt_en, rtt<2:0> (K4, xi3.odt_en, xi3.rtt<2:0>)
  - rx_en (K3, xi0.rx_en, xi1.rx_en, xi8.rx_en)
  - gate_open (K2, xi9.gate_open)
  - wl_en, wl_ck (K2/K3, xi39.wl_en, xi39.wl_ck)
  - slp (K3, mp0.slp)
- 숨기는 제어 (이름, K#):
  - ibias (K7, xi1.ibias, xi8.ibias)
  - vdd, vddq, vss, vssq (K7, 전원 및 접지)
- 블록 역할 표 (셀, 사전 행 또는 일반 박스, 확신도):
  - padesd: termination_esd, ESD 보호 소자 (높음)
  - odtleg3: termination, 저항 레그 (높음)
  - odtctl: composite, ODT 컨트롤러 (높음)
  - biasgen: bias, 바이어스 전압 생성기 (높음)
  - vrefdac: dac, VREF 64레벨 DAC (높음)
  - dqsamp: cml_buffer, CML 차동 버퍼 (높음)
  - acamp: amplifier, AC 결합 증폭기 (높음)
  - dqsrx: composite, DQS 수신기 (높음)
  - dqsgate: composite, DQS 게이팅 (높음)
  - dly3: delay_line, 3비트 딜레이 라인 (높음)
  - sbamp: vga, 단일-차동 프리앰프 (높음)
  - sadfe: strongarm, 2-탭 DFE 감지 증폭기 (높음)
  - srnand: sr_latch, SR 래치 (높음)
  - dqslice: composite, DQ 수신 슬라이스 (높음)
  - wldet: phase_detector, WL 위상 검출기 (높음)
  - rxbyte_top: composite, 바이트 수신기 최상위 (높음)
- 질문과 가정한 답 (최대 10개): 없음 (규칙 기반 전수 분류 완료)
- netlist에서 이상하다고 본 곳: 없음
