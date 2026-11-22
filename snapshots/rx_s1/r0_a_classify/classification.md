# 분류 확인 표 — dq_rx_unit (rx_s1)

```
고속 데이터 입력 : pad (ESD + ODT 패드), lb_p, lb_n (루프백 쌍)     (확신 높음 — 구조: 입력 트랜지스터 게이트 → 샘플러 데이터 입력)
클럭 입력        : ck, ckb                                          (확신 높음 — 구조: 샘플러 클럭 꼬리·리셋 게이트까지 도달)
기준             : vref (RC 필터 r0+mn0 뒤 프리앰프 둘째 입력)
고속 출력        : dout_e, dout_o
중요 제어        : rtt<2:0>, odt_en — K4 ODT 종단 / tap<3:0> — K1 DFE 탭 가중치 / tap_sgn — K1 탭 부호 (낮음) / lb_en — K2 입력 선택 / rx_en — K3 켜기 (낮음)
생략             : 제어 8개 (ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — K7 정적 트림), 바이어스 2개 (ibias, net4), 전원 4개 (vdd, vddq, vss, vssq), 블록 1개 (xi23 (rx_bias))
질문             : Q1 rx_pre / Q2 rx_en / Q3 tap_sgn / Q4 D=S 묶인 MOS / Q5 sa_dt 오프셋 코드
```

## 질문과 가정한 답 (실행 중 답할 사람이 없어 가장 그럴듯한 답을 선택)

- **Q1** [not_in_dictionary, §2.6-3, §2.7-3] `rx_pre`: 블록 역할 사전에 없는 구조입니다 (R 부하 의사 차동쌍 2개가 한 부하 공유). 일반 박스로 그릴까요? (예 / 역할 지정)
  - 확신: low (사전에 없음)
  - 가정한 답: 예 — 일반 박스 "AMP"(삼각형, 소자 구성 이름)로 그리고 확신 낮음으로 기록. VGA·CTLE 행의 특징(이득 단 가산 또는 소스 degeneration C)이 없어 사전 기호를 쓰지 않음
- **Q2** [control_class, §2.7-3] `rx_en`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (끝점이 K3(꼬리·클럭 게이트)와 K2(선택 스위치)에 모두 닿음). (K3 켜기 / K2 선택)
  - 확신: low (K2/K3 경계)
  - 가정한 답: K3 켜기 — 같은 신호가 두 입력쌍을 모두 켜고 꺼서 "고르는" 신호가 아님(lb_en이 K2). 어느 쪽이든 그림은 중요 제어 한 줄
- **Q3** [control_class, §2.7-3] `tap_sgn`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (부호 스위치: K1 가중치 / K2 선택). (K1 / K2)
  - 확신: low (K1/K2 경계)
  - 가정한 답: K1 — 탭 가중치의 부호이므로 같은 합산 가지의 세기 제어로 봄. 그림은 한 줄
- **Q4** [netlist_error_confirm, §2.7-4] `rx_pre.mn8, rx_pre.mn9, sa_dt.mn8/mn10/mn12/mn14, dq_rx_unit.mn0`: MOSFET 의 드레인과 소스가 같은 넷에 묶여 있고 게이트만 신호 노드(MOS 커패시터)입니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (D=S 묶인 소자)
  - 가정한 답: 의도됨(MOS 커패시터) — 커패시터 기호로 그리고 "MOS C"로 표기. rx_pre의 교차 접속은 netlist 대로 그림
- **Q5** [name_vs_structure, §2.6-2, §2.7-2] `sa_dt.ofp<1:0>, ofn<1:0>`: 구조는 스위치로 켜는 C 뱅크인데 이름/기능은 오프셋 트림입니다. (가변 C 뱅크로 / 오프셋 DAC로)
  - 확신: low (이름-구조 불일치 가능)
  - 가정한 답: 가변 C 뱅크로 — 구조를 따름. 스위치+MOS C 쌍을 개념 기호 가변 C로 묶고 코드는 K7 일반 제어(숨김)

## 규칙이 정한 것 (묻지 않음, §2.7-4)

- dictionary_listed_block: inv_a, inv_c, nand2_a, nand2_c, nor2_c, sr_nor, ls_lh — §2.6-1
- unused_output: dq_rx_unit: net27 (xi9.y), net29 (xi12.y) — §3.5-4 (짧은 선 + 이름표)
- bus_grouping: rtt<2:0>, tap<3:0>, ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — §2.5-7 (비트 표기가 `<n>`이라 추측 아님)

## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| rtt<2:0> | rtt<2>, rtt<1>, rtt<0> | important_control | K4 | xi21/mp2.g | 최상위 포트 (정적) | ODT 종단 코드: odt_dec(NAND + 레벨 시프터)를 지나 PMOS 스위치 mp2/mp1/mp0 게이트(enb<2:0>) → 패드에 R을 직렬로 거는 스위치 | 버스 → DEC 박스 → 버스 → 입력선 위 가변 종단 R |
| odt_en | odt_en | important_control | K4 | xi21/mp2.g | 최상위 포트 (정적) | ODT 전체 켜기(NAND로 rtt와 AND) → 같은 종단 스위치 | 한 줄 → DEC 박스 |
| tap<3:0> | tap<3>, tap<2>, tap<1>, tap<0> | important_control | K1 | xi26/mn10.g | 최상위 포트 (정적) | DFE 탭 가중치: 스위치(전류 DAC) → 귀환 쌍(hp/hn) 꼬리 전류, 귀환 쌍 입력 = 다른 경로 SR latch 출력(고속 데이터), 출력 노드에서 합산 | 버스 (Σ 위) |
| tap_sgn | tap_sgn | important_control | K1 | xi26/mn8.g | 최상위 포트 (정적) | DFE 탭 부호: 인버터 2개를 지나 sgn/sgnb로 귀환 쌍 전류가 outp/outn 어느 쪽으로 가는지 고름 | 한 줄 → 인버터 → Σ 위 (sgn, sgnb) |
| lb_en | lb_en | important_control | K2 | xi24/mn6.g | 최상위 포트 (정적) | 입력 선택: 패드 쌍(sel_m = rx_en & ~lb_en) 대 루프백 쌍(sel_l = rx_en & lb_en) 중 하나를 켬 | 한 줄 → 논리 → AMP 위 선택 핀 |
| rx_en | rx_en | important_control | K3 | xi26/mn2.g | 최상위 포트 (정적) | 수신기 켜기: Σ 꼬리 스위치(mn2), 클럭 게이트(ck_gbuf NAND), 입력쌍 꼬리 스위치 논리(sel_m/sel_l) | 한 줄 (Σ 두 개, CK GATE, 논리로 갈라짐) |
| ofe_p<1:0> | ofe_p<1>, ofe_p<0> | general_control | K7 | xi28/mn11.g | 최상위 포트 (정적) | 짝수 경로 SA 입력 노드 C 뱅크 (오프셋 트림) | 숨김 (생략 목록에 한 줄) |
| ofe_n<1:0> | ofe_n<1>, ofe_n<0> | general_control | K7 | xi28/mn7.g | 최상위 포트 (정적) | 짝수 경로 SA 입력 노드 C 뱅크 (오프셋 트림) | 숨김 (생략 목록에 한 줄) |
| ofo_p<1:0> | ofo_p<1>, ofo_p<0> | general_control | K7 | xi29/mn11.g | 최상위 포트 (정적) | 홀수 경로 SA 입력 노드 C 뱅크 (오프셋 트림) | 숨김 (생략 목록에 한 줄) |
| ofo_n<1:0> | ofo_n<1>, ofo_n<0> | general_control | K7 | xi29/mn7.g | 최상위 포트 (정적) | 홀수 경로 SA 입력 노드 C 뱅크 (오프셋 트림) | 숨김 (생략 목록에 한 줄) |
| ibias | ibias | bias | K11 | xi26/mn3.g | 바이어스 노드 | 기준 전류 입력 포트 (rx_bias 미러 다이오드 + Σ 꼬리 게이트) | 숨김 |
| net4 | net4 | bias | K11 | xi24/mn3.g | 바이어스 노드 | rx_bias 가 만든 바이어스 vbn_q → rx_pre 꼬리 게이트 | 숨김 |

- rx_en 끝점 핀: Σ 꼬리 스위치 xi26/mn2.g (K3), 클럭 게이트 xi25/xi0.b (K3), 선택 논리 xi24/mn2.g·mn6.g (K2 후보) — Q2
- tap_sgn 끝점: 인버터 xi5, xi6 → Σ 의 sgn/sgnb 게이트 xi26/mn8.g, mn9.g, mn6.g, mn7.g — Q3
- 정적 트림 ofe/ofo: 끝점 = 비교기 1단 출력 노드의 스위치 게이트, 출처 = 최상위 포트이므로 일반(K7) — 숨김

## 비고속 분류 점검 (§2.5-9)

- 기준 전압 (P1·VREF): vref — 기준 (프리앰프 vref 게이트, RC 필터 r0+mn0 뒤). ESD가 없어 P1(외부 기준 패드)은 아님, "기준 전압" 규칙 적용 → 회색 선 + 이름표, AMP 왼쪽 둘째 핀
- 상태 출력 (O1) · 명령 (K8) · 시험 (K9): 없음
- 워드 속도 디지털: 없음
- 이득·VREF 코드 (K6): 없음

## 최상위 포트 분류

| 포트 | 분류 | 설명 | 확신 |
|---|---|---|---|
| pad | data | 고속 데이터 입력 (ESD + ODT 종단이 붙은 패드) | 높음 |
| lb_p | data | 고속 데이터 입력 (루프백 쌍 +) | 높음 |
| lb_n | data | 고속 데이터 입력 (루프백 쌍 −) | 높음 |
| vref | reference | 기준 (비교기 쪽 입력 = 프리앰프 vref 게이트, RC 필터 뒤) | 높음 |
| ck | clock | 고속 클럭 입력 | 높음 |
| ckb | clock | 고속 클럭 입력 | 높음 |
| dout_e | hs_out | 고속 출력 | 높음 |
| dout_o | hs_out | 고속 출력 | 높음 |
| odt_en | K4 | ODT 켜기 | 높음 |
| rtt<2:0> | K4 | ODT 코드 | 높음 |
| tap<3:0> | K1 | DFE 탭 가중치 | 높음 |
| tap_sgn | K1 | DFE 탭 부호 | 낮음 (Q3) |
| lb_en | K2 | 입력 선택 | 높음 |
| rx_en | K3 | 수신기 켜기 | 낮음 (Q2) |
| ofe_p<1:0> | K7 일반 | 오프셋 트림 (숨김) | 높음 |
| ofe_n<1:0> | K7 일반 | 오프셋 트림 (숨김) | 높음 |
| ofo_p<1:0> | K7 일반 | 오프셋 트림 (숨김) | 높음 |
| ofo_n<1:0> | K7 일반 | 오프셋 트림 (숨김) | 높음 |
| ibias | K11 바이어스 | 기준 전류 (숨김) | 높음 |
| vdd/vddq/vss/vssq | 전원 | 숨김 | 높음 |

## 블록 역할 (§2.6, block_dictionary.json)

| 셀 | 인스턴스 | 역할 | 사전 행 | 확신 |
|---|---|---|---|---|
| esd_dq | xi20 | termination_esd | RX 종단 · ESD | high |
| odt_pu | xi21 | termination | RX 종단 · ESD (가변 종단) | high |
| odt_dec | xi22 | composite | 공통 복합 블록 (제어 허브·디코더 → DEC 박스) | high |
| rx_bias | xi23 | bias | 공통 바이어스·DAC·디지털 제어 | high |
| rx_pre | xi24 | unknown | 사전에 없음 → 일반 박스(삼각형 "AMP") | low — 빠진 특징: VGA: 이득 단 가산/degeneration R 코드 없음; CTLE: 소스 degeneration C 없음 |
| ck_gbuf | xi25 | composite | 공통 복합 블록 | high |
| dfe_sum | xi26, xi27 | summer | RX/TX Summer (DFE·FFE) | high |
| sa_dt | xi28, xi29 | comparator | RX 비교기 · 샘플러 (double-tail) | high |
| sr_nor | xi30, xi31 | sr_latch | 공통 SR latch | high |
| inv_a | xi0, xi2, xi4, xi5, xi6, xi7, xi9, xi10, xi12 | inverter | 공통 논리 게이트 (INV) | high |
| inv_c | xi8, xi11 | inverter | 공통 논리 게이트 (INV) | high |
| nand2_a | xi1, xi3 | nand | 공통 논리 게이트 (NAND) | high |
| nand2_c | xi0, xi1 | nand | 공통 논리 게이트 (NAND) | high |
| nor2_c | xi0, xi1 | nor | 공통 논리 게이트 (NOR) | high |
| ls_lh | xi3, xi4, xi5 | ls | 공통 레벨 시프터 (LS) | high |
| dq_rx_unit | (top) | general | 공통 복합 블록 (예외: 하위 rx_pre 가 사전에 없음) | low — 빠진 특징: 하위 rx_pre 가 사전 행 아님 → 복합 블록 행 조건 불충족 |
| (virtual) r0+mn0 | (top) | lpf | 공통 RC 평균기 | high |
| (virtual) sa_dt/stage1 | xi28, xi29 | comparator_stage1 | 비교기 1단 (가상 블록) | high |
| (virtual) sa_dt/stage2 | xi28, xi29 | comparator_stage2 | 비교기 2단 (가상 블록) | high |

## netlist 에서 이상하다고 본 곳

- rx_pre mn8 (D=S=outp, G=inp), mn9 (D=S=outn, G=vref): 입력과 반대편 출력을 잇는 교차 MOS 커패시터 (Q4)
- sa_dt mn8/mn10/mn12/mn14, dq_rx_unit mn0: D=S 묶인 MOS 커패시터 (Q4, 의도로 보임)
- sa_dt 의 mp2 헤더 게이트는 ck 의 반전(net60); 1단 리셋 PMOS(mp0/mp1)는 ck 로 직접 구동 — 정상
- dfe_sum 의 sgn/sgnb 는 top 에서 tap_sgn 인버터 두 개로 만들어짐: sgnb = ~tap_sgn(net105), sgn = tap_sgn(net106) — 이름과 반대로 보이지만 netlist 대로
- 짝수 경로 Σ(xi26)의 귀환 입력은 홀수 경로 SR(net16/net17), 홀수 경로 Σ(xi27)는 짝수 경로 SR(net14/net15) — 반속도 루프 풀림 구조, 이상 아님
