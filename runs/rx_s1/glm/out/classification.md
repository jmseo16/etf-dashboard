# 분류 확인 표 — dq_rx_unit

```
고속 데이터 입력 : pad (확신 높음 — 구조: ESD·ODT 연결, 전치증폭기 입력쌍 게이트)
클럭 입력        : ck, ckb (확신 높음 — 구조: 클럭 게이팅 버퍼 거쳐 double-tail 센스앰프 꼬리 구동)
고속 출력        : dout_e, dout_o (확신 높음 — even/odd SR 래치 출력 구동 인버터 체인 출력)
중요 제어 (선/버스) : tap<3:0> — K1 DFE 탭 계수 가중치 (확신 높음)
                   tap_sgn — K1 DFE 탭 극성 (확신 높음)
                   lb_en — K2 루프백 선택 (확신 높음)
                   rx_en — K3 수신기 켜기/끄기 (확신 높음)
                   odt_en — K4 종단 켜기 (확신 높음)
                   rtt<2:0> — K4 종단 코드 (확신 높음)
숨기는 제어 (다비트) : ofe_p<1:0> — K7 Even SA P측 오프셋 트림
                   ofe_n<1:0> — K7 Even SA N측 오프셋 트림
                   ofo_p<1:0> — K7 Odd SA P측 오프셋 트림
                   ofo_n<1:0> — K7 Odd SA N측 오프셋 트림
```

## 질문과 가정한 답 (§2.7)

- **Q1** [port_role, §2.7-2, §2.7-3] `vref`: 포트 `vref`는 기준 전압 입력입니까? (기준 전압 / 바이어스)
  - 확신: low (단일 종단 수신기의 비교 기준선)
  - 가정한 답: 기준 전압 입력 — pad와 함께 수신 차동 신호의 음의 입력으로 기능.
- **Q2** [control_class, §2.7-3] `lb_en`: `lb_en`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (시험 모드 선택 스위치 구동). (중요 / 일반)
  - 확신: low (모드 제어)
  - 가정한 답: 중요 제어 (K2) — 고속 신호 경로 MUX 선택 신호.
- **Q3** [control_class, §2.7-3] `odt_en`: `odt_en`: 중요 제어와 일반 제어 중 어느 쪽인지 구조로 정할 수 없습니다 (종단 저항 인에이블 스위치 구동). (중요 / 일반)
  - 확신: low (모드 제어)
  - 가정한 답: 중요 제어 (K4) — 패드 종단 온/오프 제어.
- **Q4** [name_vs_structure, §2.6-2, §2.7-2] `rx_pre`: `rx_pre`: 구조는 차동 증폭기 및 루프백 MUX인데 이름/기능은 전치 증폭기입니다. (증폭기+MUX로 / 전치증폭기로)
  - 확신: low (사전 VGA/CTLE와 차동 증폭기+MUX 혼합)
  - 가정한 답: 전치증폭기 — 일반 박스 PREAMP로 그리고 내부 구성 표시.
- **Q5** [netlist_error_confirm, §2.7-4] `xi9, xi12`: `xi9, xi12`: 출력 net27, net29가 다른 회로에 연결되지 않고 플로팅됨. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (더미 부하 추정)
  - 가정한 답: 의도됨 — 더미 부하 인버터로 간주하고 짧은 선과 이름표로 표시.

## 규칙이 정한 것 (묻지 않음, §2.7-4)

- dictionary_listed_block: inv_a, inv_c, nand2_a, nand2_c, nor2_c, ls_lh, sr_nor — §2.6-1 (논리 게이트·SR latch·LS는 사전에 있음) → 사전 행으로 그림
- unused_output: net27, net29 — §3.5-4 (미사용 출력: 짧은 선 + 이름표)
- bus_grouping: tap<3:0>, rtt<2:0>, ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> — §2.5-7 (같은 기능의 비트는 버스 하나)

## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| tap<3:0> | tap<3>, tap<2>, tap<1>, tap<0> | important_control | K1 | xi26/mn10.g | 최상위 포트 | DFE 탭 계수 가중치 — IDAC 스위치 → 탭 쌍 꼬리 전류, Σ 출력에서 합산 | 버스 (사선 + 이름) |
| tap_sgn | tap_sgn | important_control | K1 | xi5/mn0.g | 최상위 포트 | DFE 탭 계수 극성 제어 — 극성 반전 스위치 게이트 구동 | 선 (단일 비트) |
| lb_en | lb_en | important_control | K2 | xi0/mn0.g | 최상위 포트 | 루프백 선택 신호 — pad/vref 경로와 lb_p/lb_n 루프백 경로 간 상보 선택 | 선 (단일 비트) |
| rx_en | rx_en | important_control | K3 | xi25/xi0/mn1.g | 최상위 포트 | 수신기 켜기/끄기 — 클럭 게이팅 버퍼, 프리앰프, DFE summer 꼬리 인에이블 | 선 (단일 비트) |
| odt_en | odt_en | important_control | K4 | xi22/xi2/mn0.g | 최상위 포트 | 종단 켜기/끄기 — ODT 디코더 NAND 입력 | 선 (단일 비트) |
| rtt<2:0> | rtt<2>, rtt<1>, rtt<0> | important_control | K4 | xi22/xi2/mn1.g | 최상위 포트 | 가변 종단 저항 코드 — ODT 디코더 거쳐 패드 풀업 저항 스위치 제어 | 버스 (사선 + 이름) |
| ofe_p<1:0> | ofe_p<1>, ofe_p<0> | general_control | K7 | xi28/mn11.g | 최상위 포트 | 센스앰프 (even, P측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofe_n<1:0> | ofe_n<1>, ofe_n<0> | general_control | K7 | xi28/mn7.g | 최상위 포트 | 센스앰프 (even, N측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofo_p<1:0> | ofo_p<1>, ofo_p<0> | general_control | K7 | xi29/mn11.g | 최상위 포트 | 센스앰프 (odd, P측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |
| ofo_n<1:0> | ofo_n<1>, ofo_n<0> | general_control | K7 | xi29/mn7.g | 최상위 포트 | 센스앰프 (odd, N측) 오프셋 트림 제어 | 숨김 (생략 목록에 한 줄) |

## 비고속 분류 점검 (§2.5-9)

- 기준 전압 (P1·VREF): vref — 외부 포트에서 RC 저역통과 필터(r0, mn0) 거쳐 프리앰프(rx_pre) 한쪽 입력으로 공급되는 기준 전압
- 상태 출력 (O1) · 명령 (K8) · 시험 (K9): 없음
- 워드 속도 디지털: 없음
- 이득·VREF 코드 (K6): 없음

## 최상위 포트 분류

| 포트 | 분류 | K# | 근거 |
|---|---|---|---|
| pad | data |  | 주 고속 입력 (구조: ESD, ODT, 프리앰프 입력쌍 게이트) |
| vref | reference |  | 판정 기준 전압 (비고속 아날로그, 회색 실선 VREF) |
| ck | clock |  | 차동 고속 클럭 입력 (구조: 클럭 게이팅 버퍼 거쳐 SA 클럭 꼬리 구동) |
| ckb | clock |  | 차동 고속 클럭 입력 (구조: 클럭 게이팅 버퍼 거쳐 SA 클럭 꼬리 구동) |
| lb_p | data |  | 루프백 시험 고속 입력 (프리앰프 루프백 차동쌍 게이트) |
| lb_n | data |  | 루프백 시험 고속 입력 (프리앰프 루프백 차동쌍 게이트) |
| lb_en | important_control | K2 | pad vs 루프백 선택 스위치 MUX 제어 |
| rx_en | important_control | K3 | 수신기 활성화 및 클럭 게이팅 enable 제어 |
| odt_en | important_control | K4 | ODT 종단 활성화 제어 |
| rtt<2> | important_control | K4 | ODT 종단 저항 코드 bit 2 |
| rtt<1> | important_control | K4 | ODT 종단 저항 코드 bit 1 |
| rtt<0> | important_control | K4 | ODT 종단 저항 코드 bit 0 |
| tap<3> | important_control | K1 | DFE summer 탭 가중치 코드 bit 3 |
| tap<2> | important_control | K1 | DFE summer 탭 가중치 코드 bit 2 |
| tap<1> | important_control | K1 | DFE summer 탭 가중치 코드 bit 1 |
| tap<0> | important_control | K1 | DFE summer 탭 가중치 코드 bit 0 |
| tap_sgn | important_control | K1 | DFE summer 탭 극성 부호 제어 |
| ofe_p<1> | general_control | K7 | Even 센스앰프 P측 오프셋 트림 bit 1 |
| ofe_p<0> | general_control | K7 | Even 센스앰프 P측 오프셋 트림 bit 0 |
| ofe_n<1> | general_control | K7 | Even 센스앰프 N측 오프셋 트림 bit 1 |
| ofe_n<0> | general_control | K7 | Even 센스앰프 N측 오프셋 트림 bit 0 |
| ofo_p<1> | general_control | K7 | Odd 센스앰프 P측 오프셋 트림 bit 1 |
| ofo_p<0> | general_control | K7 | Odd 센스앰프 P측 오프셋 트림 bit 0 |
| ofo_n<1> | general_control | K7 | Odd 센스앰프 N측 오프셋 트림 bit 1 |
| ofo_n<0> | general_control | K7 | Odd 센스앰프 N측 오프셋 트림 bit 0 |
| ibias | bias | K11 | 정적 바이어스 전류 입력 (rx_bias 연결) |
| dout_e | data |  | Even 데이터 고속 출력 (인버터 체인 구동) |
| dout_o | data |  | Odd 데이터 고속 출력 (인버터 체인 구동) |
| vdd | power |  | 코어 전원 공급 레일 |
| vddq | power |  | IO/전치증폭기 전원 공급 레일 |
| vss | power |  | 코어 접지 레일 |
| vssq | power |  | IO/전치증폭기 접지 레일 |

## 최상위 내부 넷 분류

| 넷 | 분류 | 근거 |
|---|---|---|
| net1 | data | pad에서 ESD 직렬 저항 r0 거쳐 프리앰프 inp로 전달되는 고속 데이터 |
| net2<2:0> | general_control | ODT 디코더 xi22에서 ODT 풀업 스위치 xi21로 전달되는 버스 제어 (중요 제어 rtt/odt_en에서 디코드됨) |
| net3 | reference | vref에서 RC 필터(r0, mn0) 거쳐 프리앰프 vref 핀으로 전달되는 필터링된 기준 전압 |
| net4 | bias | rx_bias에서 프리앰프 바이어스 꼬리 게이트 vbn으로 전달되는 바이어스 전압 |
| net6 | data | 프리앰프 outp 차동 출력 (even/odd summer inp 구동) |
| net7 | data | 프리앰프 outn 차동 출력 (even/odd summer inn 구동) |
| net8 | clock | 클럭 게이팅 버퍼 cko 출력 (Even 슬라이스 센스앰프 클럭) |
| net9 | clock | 클럭 게이팅 버퍼 ckob 출력 (Odd 슬라이스 센스앰프 클럭) |
| net10 | data | Even DFE summer outp (Even 센스앰프 inp 구동) |
| net11 | data | Even DFE summer outn (Even 센스앰프 inn 구동) |
| net12 | data | Odd DFE summer outp (Odd 센스앰프 inp 구동) |
| net13 | data | Odd DFE summer outn (Odd 센스앰프 inn 구동) |
| net14 | data | Even SR latch q 출력 (Even 인버터 체인 입력 및 Odd summer 탭 귀환) |
| net15 | data | Even SR latch qb 출력 (Odd summer 탭 귀환 및 xi9 미사용 출력) |
| net16 | data | Odd SR latch q 출력 (Odd 인버터 체인 입력 및 Even summer 탭 귀환) |
| net17 | data | Odd SR latch qb 출력 (Even summer 탭 귀환 및 xi12 미사용 출력) |
| net18 | data | Even 센스앰프 outp (Even SR 래치 s 입력) |
| net19 | data | Even 센스앰프 outn (Even SR 래치 r 입력) |
| net24 | data | Odd 센스앰프 outp (Odd SR 래치 s 입력) |
| net25 | data | Odd 센스앰프 outn (Odd SR 래치 r 입력) |
| net26 | data | Even 출력 인버터 중간 노드 (xi7.y → xi8.a) |
| net27 | unused | Even qb 반전 더미 출력 (xi9.y) — 부하 없음 |
| net28 | data | Odd 출력 인버터 중간 노드 (xi10.y → xi11.a) |
| net29 | unused | Odd qb 반전 더미 출력 (xi12.y) — 부하 없음 |
| net100..net104 | general_control | 제어 게이팅 논리 내부 넷 |
| net105..net106 | general_control | 탭 극성 버퍼 내부 넷 |

## 블록 역할 대응 표 (명세서 §2.6)

| 셀 | 인스턴스 | 사전 행 | 기호 | 확신도 | 질문 |
|---|---|---|---|---|---|
| inv_a | xi0, xi2, xi4, xi5, xi6, xi7, xi9, xi10, xi12, xi23/xi0 | 공통 논리 게이트 (INV) | 인버터 | high |  |
| inv_c | xi8, xi11, xi25/xi2, xi25/xi3, xi28/xi0, xi29/xi0 | 공통 논리 게이트 (INV) | 인버터 | high |  |
| nand2_a | xi1, xi3, xi22/xi0, xi22/xi1, xi22/xi2 | 공통 논리 게이트 (NAND) | 박스(셀 이름) + 출력 동그라미 | high |  |
| nand2_c | xi25/xi0, xi25/xi1 | 공통 논리 게이트 (NAND) | 박스(셀 이름) + 출력 동그라미 | high |  |
| nor2_c | xi30/xi0, xi30/xi1, xi31/xi0, xi31/xi1 | 공통 논리 게이트 (NOR) | 박스(셀 이름) + 출력 동그라미 | high |  |
| ls_lh | xi22/xi3, xi22/xi4, xi22/xi5 | 공통 Level Shifter | 박스(셀 이름) | high |  |
| esd_dq | xi20 | RX 종단 · ESD | 입력선 위 R/ESD 표시 | high |  |
| odt_pu | xi21 | RX 종단 · ESD | 입력선 위 가변 종단 R 표시 | high |  |
| odt_dec | xi22 | 제어 디코더 | box (cell name) | high | Q3 |
| rx_bias | xi23 | 공통 바이어스 발생기 | omit | high |  |
| rx_pre | xi24 | 일반 박스 (사전 외) | box (cell name) | low | Q4 |
| dfe_sum | xi26, xi27 | RX/TX Summer (DFE·FFE) | Σ | high |  |
| sa_dt | xi28, xi29 | 동적 비교기 (Double-Tail SA) | 삼각형 SA + 클럭 | high |  |
| sr_nor | xi30, xi31 | 공통 SR latch | 박스(셀 이름) | high |  |
| ck_gbuf | xi25 | Clock 게이팅 버퍼 | 삼각형 버퍼 + 게이트 입력 | high |  |
| dq_rx_unit | (최상위) | 최상위 블록 | 박스 | high |  |
