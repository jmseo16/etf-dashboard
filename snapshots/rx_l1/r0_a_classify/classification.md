# 분류 확인 표 — rxbyte_top (rx_l1)

```
고속 데이터 입력 : dq<7:0> (ESD + ODT 패드 8개)           (확신 높음)
클럭 입력        : dqs_t, dqs_c                          (확신 높음 — DQS 수신기·게이트·지연·클럭 트리를 거쳐 샘플러 클럭 꼬리/리셋에 도달)
고속 출력        : qr<7:0>, qf<7:0>
상태 출력        : wl_out (O1)
중요 제어        : odt_en, rtt<2:0> K4 / t1w<2:0>, t2w<1:0> K1 / vrc<5:0> K6 / rx_en, slp, gate_open, wl_en K3 / wl_ck K8 (낮음)
생략             : 제어 3개 (ddl<2:0> K7), 바이어스 2개 (ibias, net203), 전원 (vdd, vddq, vss, vssq, 가상 전원 net200), 블록 1개 (xi1 (biasgen))
질문             : Q1 wl_ck / Q2 ckbuf 출력 단락 / Q3 더미 슬라이스 xi38 / Q4 acamp / Q5 sbamp / Q6 sadfe / Q7 안테나 다이오드 / Q8 버스 표기
```

## 질문과 가정한 답

- **Q1** [port_role, §2.7-2] 포트 `wl_ck`는 고속 데이터 입력입니까? (예 / 클럭 / 제어 / 바이어스)
  - 확신: low (역할이 구조로 정해지지 않음)
  - 가정한 답: 제어 (K8) — 단일 디지털 포트라 §2.4-1 에 따라 데이터가 아님. wldet 플립플롭의 D 입력(DQS 파생 클럭으로 샘플링)이라 명령 한 줄로 그림
- **Q2** [netlist_error_confirm, §2.7-4] `xi14/xi15, xi16/xi17, xi18/xi19, xi20/xi21 (ckbuf)`: 같은 입력에서 같은 출력을 두 인스턴스가 함께 구동합니다 (출력 단락). netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (출력 단락)
  - 가정한 답: 의도됨 (병렬 구동으로 세기 ×2) — 반복 인스턴스로 합쳐 `xi14 … xi15` 로 그림
- **Q3** [netlist_error_confirm, §2.7-4] `xi38 (dqslice)`: 입력이 모두 전원에 묶이고 출력이 쓰이지 않습니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (상수 입력, 출력 미사용)
  - 가정한 답: 의도됨 (클럭 부하 맞춤용 더미/복제 슬라이스) — 블록으로 그리고 상수 입력은 회색 선 + 이름표
- **Q4** [not_in_dictionary, §2.6-3, §2.7-3] `acamp`: 블록 역할 사전에 없는 구조입니다 (AC 결합 인버터 증폭기). 일반 박스로 그릴까요? (예 / 역할 지정)
  - 확신: low (사전에 없음)
  - 가정한 답: 예 — 일반 박스
- **Q5** [not_in_dictionary, §2.6-3, §2.7-3] `sbamp`: 블록 역할 사전에 없는 구조입니다 (인버터형 단일 입력 증폭기 + enable). 일반 박스로 그릴까요? (예 / 역할 지정)
  - 확신: low (사전에 없음)
  - 가정한 답: 예 — 삼각형 "AMP" 일반 박스
- **Q6** [not_in_dictionary, §2.6-3, §2.7-3] `sadfe`: StrongARM 행의 특징은 모두 있고 합산 탭 쌍이 더 붙었습니다. 비교기(SA) 기호로 그릴까요? (예 / 역할 지정)
  - 확신: low (사전 행 확장)
  - 가정한 답: 예 — SA 삼각형에 탭 입력(왼쪽)·가중치 버스(위) 핀을 더해 그림
- **Q7** [netlist_error_confirm, §2.7-4] `d0, d1`: 클럭 선에 다이오드가 붙어 있습니다. netlist 오류일 수 있습니다. 의도된 것입니까? (의도됨 / netlist 오류)
  - 확신: low (패드 밖 다이오드)
  - 가정한 답: 의도됨 (안테나 보호) — 클럭 선에 매달린 다이오드 기호 "ESD"로 그림
- **Q8** [bus_notation_guess, §2.5-7] `t1w2…`: 비트 표기가 `<n>`이 아니어서 이름 끝 숫자를 비트 번호로 읽어 t1w<2:0>, t2w<1:0>, vrc<5:0>, ddl<2:0>, rtt<2:0>, dq<7:0>, qr<7:0>, qf<7:0>로 묶었습니다. 맞습니까? (예 / 표기 지정)
  - 확신: low (비트 표기 추측)
  - 가정한 답: 예

## 규칙이 정한 것 (묻지 않음)

- dictionary_listed_block: invx1, invx4, nand2x1, nand2x2, lvlup(LS), dly3(DLY), srnand(SR latch), lat_tg/dfftg(latch/DFF), mux2tg(MUX) — §2.6-1
- unused_output: xi38 의 qr/qf (net224, net225) — 짧은 선 + 이름표 (§3.5-4)
- bus_grouping: §2.5-7

## 제어 분류 (K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| odt_en | odt_en | important_control | K4 | xi6/mp2.g | 최상위 포트 (정적) | ODT 켜기 (odtctl NAND) | 한 줄 → DEC 박스 |
| rtt<2:0> | rtt<2>, rtt<1>, rtt<0> | important_control | K4 | xi6/mp2.g | 최상위 포트 (정적) | ODT 코드 → odtctl → 모든 DQ/DQS 패드의 풀업 다리 PMOS 게이트 | 버스 → DEC 박스 |
| t1w<2:0> | t1w<2>, t1w<1>, t1w<0> | important_control | K1 | xi30/xi4/mn12.g | 최상위 포트 (정적) | DFE 탭1 가중치: 스위치 → 탭1 쌍 꼬리, 탭 입력 = 상대 경로 SR latch 출력, 비교기 노드에서 합산 | 버스 (SA 위) |
| t2w<1:0> | t2w<1>, t2w<0> | important_control | K1 | xi30/xi4/mn22.g | 최상위 포트 (정적) | DFE 탭2 가중치: 탭 입력 = 자기 경로 SR latch 출력 | 버스 (SA 위) |
| vrc<5:0> | vrc<5>, vrc<4>, vrc<3>, vrc<2>, vrc<1>, vrc<0> | important_control | K6 | xi2/mp11.g | 최상위 포트 (정적) | 비교기 기준 레벨 코드 (VREF DAC): 인버터 → 스위치 PMOS → 분압 저항, 8개 슬라이스가 같은 vref(net204)를 공유 | 버스 → VREF 박스 |
| rx_en | rx_en | important_control | K3 | xi30/xi2/mn6.g | 최상위 포트 (정적) | 수신기 켜기: 레벨 시프터(lvlup) → 각 슬라이스 sbamp en/enb, dqsamp·acamp 꼬리 스위치 | 한 줄 (분기) |
| slp | slp | important_control | K3 | mp0.g | 최상위 포트 (정적) | 슬립: 슬라이스 전원(net200) 헤더 스위치 | 한 줄 |
| gate_open | gate_open | important_control | K3 | xi9/xi0/mn0.g | 최상위 포트 (정적) | DQS 게이트 열기: 클럭 게이트 래치 enable (게이트되는 클럭이 고속이므로 K3) | 한 줄 |
| wl_en | wl_en | important_control | K3 | xi39/xi0.b | 최상위 포트 (정적) | WL 검출기 클럭 게이트 enable | 한 줄 |
| wl_ck | wl_ck | important_control | K8 | xi39/xi2/mn0.g | 최상위 포트 (정적) | WL 검출 플립플롭 D 입력 (샘플링 대상 신호) | 한 줄 (낮은 확신) |
| ddl<2:0> | ddl<2>, ddl<1>, ddl<0> | general_control | K7 | xi10/xi1/mn0.g | 최상위 포트 (정적) | DQS 지연선 탭 선택 (같은 지연 소자의 탭 고르기 = 미세 트림) | 숨김 |
| ibias | ibias | bias | K11 | xi1/mn0.g | 바이어스 노드 | 기준 전류 입력 | 숨김 |
| net203 | net203 | bias | K11 | xi2/mp10.g | 바이어스 노드 | biasgen 의 vbp → vrefdac 전류원 게이트 | 숨김 |

## 비고속 분류 점검

- 기준 전압 (P1·VREF): net204 — vrefdac 가 만든 기준 전압, 코드 vrc<5:0> (K6)
- 상태 출력 (O1) · 명령 (K8) · 시험 (K9): wl_out O1, wl_ck K8(낮음)
- 워드 속도 디지털: 없음
- 이득·VREF 코드 (K6): vrc<5:0>

## 최상위 포트 분류

| 포트 | 분류 | 설명 | 확신 |
|---|---|---|---|
| dq7..dq0 | data | 고속 데이터 입력 (ESD + ODT 패드) ×8 | 높음 |
| dqs_t, dqs_c | clock | 고속 클럭(스트로브) 입력 (ESD + ODT, 클럭 트리를 거쳐 샘플러 클럭 꼬리·리셋에 도달) | 높음 |
| qr7..qr0, qf7..qf0 | hs_out | 고속 출력 ×16 | 높음 |
| wl_out | O1 | 상태 출력 (플립플롭이 구동) | 높음 |
| odt_en, rtt<2:0> | K4 | ODT | 높음 |
| t1w<2:0>, t2w<1:0> | K1 | DFE 탭 가중치 | 높음 |
| vrc<5:0> | K6 | VREF 코드 | 높음 |
| rx_en, slp, gate_open, wl_en | K3 | 켜기 | rx_en/slp/gate_open 높음, wl_en 높음 |
| wl_ck | K8 | 낮은 확신 (Q1) | 낮음 |
| ddl<2:0> | K7 일반 | 숨김 | 높음 |
| ibias | K11 | 숨김 | 높음 |
| vdd/vddq/vss/vssq | 전원 | 숨김 | 높음 |

## 블록 역할

| 셀 | 인스턴스 | 역할 | 사전 행 | 확신 |
|---|---|---|---|---|
| padesd | dqslice.xi0, rxbyte_top.xi4, rxbyte_top.xi5 | termination_esd | RX 종단 · ESD | high |
| odtleg3 | dqslice.xi1, rxbyte_top.xi6, rxbyte_top.xi7 | termination | RX 종단 (가변) | high |
| odtctl | rxbyte_top.xi3 | composite | 공통 복합 블록 (DEC 박스) | high |
| biasgen | rxbyte_top.xi1 | bias | 바이어스 | high |
| vrefdac | rxbyte_top.xi2 | dac | 기준 전압 DAC "VREF" 박스 | high |
| lvlup | rxbyte_top.xi0, odtctl.xi3..xi5 | ls | 공통 레벨 시프터 | high |
| dqsrx | rxbyte_top.xi8 | composite | 공통 복합 블록 (하위에 사전에 없는 acamp) | low — 빠진 특징: 하위 acamp 가 사전 행 아님 |
| dqsamp | dqsrx.xi0 | ctle? | R 부하 차동 증폭기 | low — 빠진 특징: VGA/CTLE 특징 없음 → 일반 박스 |
| acamp | dqsrx.xi1, dqsrx.xi2 | unknown | 사전에 없음 | low — 빠진 특징: AC 결합 인버터 증폭기 |
| dqsgate | rxbyte_top.xi9 | composite | 공통 복합 블록 (ICG 류) | high |
| dly3 | rxbyte_top.xi10, xi11 | dly | 공통 지연 셀 (DLY) | high |
| ckbuf | rxbyte_top.xi12..xi23 | composite | Clock 버퍼 (CMOS 인버터 2단) | high |
| dqslice | rxbyte_top.xi30..xi37, xi38 | composite | 공통 복합 블록 (하위에 sbamp·sadfe 일반/변형) | low — 빠진 특징: 하위 sbamp 가 사전 행 아님 |
| sbamp | dqslice.xi2, dqslice.xi3 | unknown | 사전에 없음 | low — 빠진 특징: 인버터형 증폭기 + enable |
| sadfe | dqslice.xi4, dqslice.xi6 | comparator | RX 비교기·샘플러 (StrongARM) + 탭 쌍 | low — 빠진 특징: 탭 쌍(합산) — 사전 행 확장 |
| srnand | dqslice.xi5, dqslice.xi7 | sr_latch | 공통 SR latch | high |
| wldet | rxbyte_top.xi39 | composite | 공통 복합 블록 | high |
| dfftg | wldet.xi2 | dff | 공통 Latch·DFF (TG DFF) | high |
| lat_tg | dqsgate.xi0, dqsgate.xi1 | latch | 공통 Latch (TG) | high |
| mux2tg | dly3.xi1,5,11 | mux | 공통 MUX | high |
| invx1/invx4/nand2x1/nand2x2/dlybuf | 여러 곳 | inverter/nand | 공통 논리 게이트 | high |
| rxbyte_top | (top) | general | 복합 블록 (예외: 하위에 사전에 없는 블록) | low — 빠진 특징: dqsrx/dqslice 가 사전 밖 하위를 가짐 |

## netlist 에서 이상하다고 본 곳

- ckbuf 병렬 출력 단락 (Q2), 더미 슬라이스 xi38 (Q3), 안테나 다이오드 (Q7)
- 상위의 mp0 가 만드는 net200 은 PMOS 벌크로 쓰이는 가상 전원(헤더)이라 전원으로 분류
- dqslice 안 두 sadfe 는 대칭 구조: 한 경로의 h1 = 상대 SR 출력, h2 = 자기 SR 출력 (반속도 2탭 DFE)
