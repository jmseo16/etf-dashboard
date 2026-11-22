# 분류 확인 표 — rxbyte_top

```
고속 데이터 입력 : dq0, dq1, dq2, dq3, dq4, dq5, dq6, dq7 (확신 높음 — 구조: DQ 슬라이스 입력 패드 + ESD/ODT)
클럭 입력        : dqs_t, dqs_c (확신 높음 — 구조: 차동 DQS 스트로브 수신기, 래치 및 StrongARM 트리 도달)
고속 출력        : qr0, qr1, qr2, qr3, qr4, qr5, qr6, qr7, qf0, qf1, qf2, qf3, qf4, qf5, qf6, qf7 (확신 높음 — 구조: 상승/하강 데이터 래치 출력 및 WL 검출 출력)
중요 제어 (버스) : rx_en — K3 / gate_open — K2 / wl_en — K2 / wl_ck — K2 / slp — K3 / odt_en — K4 / rtt<2:0> — K4 / vrc<5:0> — K5 / t1w<2:0> — K1 / t2w<1:0> — K1 / ddl<2:0> — K6 / wl_out — K2
생략             : 바이어스 1개 (ibias), 전원 4개 (vdd, vddq, vss, vssq)
질문             : 없음 (규칙 기반 전수 분류 완료)
```

## 질문과 가정한 답 (§2.7)
- 없음 (규칙 기반 전수 분류 완료)

## 규칙이 정한 것 (묻지 않음, §2.7-4)
- dictionary_listed_block: invx1, invx4, nand2x1, nand2x2, lvlup, lat_tg, dfftg, mux2tg, dlybuf, ckbuf, srnand — §2.6-1

## 제어 분류 (§2.5-9: 그린 제어마다, 숨긴 다비트 제어마다 K#·끝점 핀·출처)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 기능 | 그림 |
|---|---|---|---|---|---|---|---|
| rx_en | rx_en | important_control | K3 | xi0/mn0.g | 최상위 포트 | 수신기 활성화 | 선 (단일 비트) |
| gate_open | gate_open | important_control | K2 | xi9/xi0/xi0/mn0.g | 최상위 포트 | DQS 게이팅 윈도우 | 선 (단일 비트) |
| wl_en | wl_en | important_control | K2 | xi39/xi0/mn1.g | 최상위 포트 | Write Leveling 인에이블 | 선 (단일 비트) |
| wl_ck | wl_ck | important_control | K2 | xi39/xi2/xi0/mn0.g | 최상위 포트 | Write Leveling 클럭 | 선 (단일 비트) |
| slp | slp | important_control | K3 | mp0.g | 최상위 포트 | 수신기 슬립 제어 | 선 (단일 비트) |
| odt_en | odt_en | important_control | K4 | xi3/xi2/mn0.g | 최상위 포트 | 종단 인에이블 | 선 (단일 비트) |
| rtt<2:0> | rtt2, rtt1, rtt0 | important_control | K4 | xi3/xi2/mn1.g | 최상위 포트 | ODT 임피던스 코드 | 버스 (사선 + 이름) |
| vrc<5:0> | vrc5, vrc4, vrc3, vrc2, vrc1, vrc0 | important_control | K5 | xi2/xi0/mn0.g | 최상위 포트 | VREF DAC 설정 코드 | 버스 (사선 + 이름) |
| t1w<2:0> | t1w2, t1w1, t1w0 | important_control | K1 | xi30/xi4/mn12.g | 최상위 포트 | DFE 탭 1 가중치 | 버스 (사선 + 이름) |
| t2w<1:0> | t2w1, t2w0 | important_control | K1 | xi30/xi4/mn22.g | 최상위 포트 | DFE 탭 2 가중치 | 버스 (사선 + 이름) |
| ddl<2:0> | ddl2, ddl1, ddl0 | important_control | K6 | xi10/xi1/mn0.g | 최상위 포트 | DQS 딜레이 제어 | 버스 (사선 + 이름) |

## 최상위 포트 분류

| 포트 | 분류 | K# | 근거 |
|---|---|---|---|
| dq0 | data |  | 8비트 고속 데이터 입력 비트 0 |
| dq1 | data |  | 8비트 고속 데이터 입력 비트 1 |
| dq2 | data |  | 8비트 고속 데이터 입력 비트 2 |
| dq3 | data |  | 8비트 고속 데이터 입력 비트 3 |
| dq4 | data |  | 8비트 고속 데이터 입력 비트 4 |
| dq5 | data |  | 8비트 고속 데이터 입력 비트 5 |
| dq6 | data |  | 8비트 고속 데이터 입력 비트 6 |
| dq7 | data |  | 8비트 고속 데이터 입력 비트 7 |
| dqs_t | clock |  | 차동 DQS 고속 클럭 스트로브 입력 (True) |
| dqs_c | clock |  | 차동 DQS 고속 클럭 스트로브 입력 (Complement) |
| qr0 | data |  | 라이징 에지 복구 데이터 출력 비트 0 |
| qr1 | data |  | 라이징 에지 복구 데이터 출력 비트 1 |
| qr2 | data |  | 라이징 에지 복구 데이터 출력 비트 2 |
| qr3 | data |  | 라이징 에지 복구 데이터 출력 비트 3 |
| qr4 | data |  | 라이징 에지 복구 데이터 출력 비트 4 |
| qr5 | data |  | 라이징 에지 복구 데이터 출력 비트 5 |
| qr6 | data |  | 라이징 에지 복구 데이터 출력 비트 6 |
| qr7 | data |  | 라이징 에지 복구 데이터 출력 비트 7 |
| qf0 | data |  | 폴링 에지 복구 데이터 출력 비트 0 |
| qf1 | data |  | 폴링 에지 복구 데이터 출력 비트 1 |
| qf2 | data |  | 폴링 에지 복구 데이터 출력 비트 2 |
| qf3 | data |  | 폴링 에지 복구 데이터 출력 비트 3 |
| qf4 | data |  | 폴링 에지 복구 데이터 출력 비트 4 |
| qf5 | data |  | 폴링 에지 복구 데이터 출력 비트 5 |
| qf6 | data |  | 폴링 에지 복구 데이터 출력 비트 6 |
| qf7 | data |  | 폴링 에지 복구 데이터 출력 비트 7 |
| wl_out | important_control | K2 | Write Leveling 위상 판정 결과 출력 |
| rx_en | important_control | K3 | 수신기 활성화 제어 |
| gate_open | important_control | K2 | DQS 게이팅 윈도우 제어 |
| wl_en | important_control | K2 | Write Leveling 활성화 |
| wl_ck | important_control | K2 | Write Leveling 기준 클럭 |
| slp | important_control | K3 | 수신기 슬립/파워다운 제어 |
| odt_en | important_control | K4 | 온다이 터미네이션 활성화 |
| rtt2 | important_control | K4 | ODT 임피던스 코드 비트 2 |
| rtt1 | important_control | K4 | ODT 임피던스 코드 비트 1 |
| rtt0 | important_control | K4 | ODT 임피던스 코드 비트 0 |
| vrc5 | important_control | K5 | VREF DAC 전압 설정 코드 비트 5 |
| vrc4 | important_control | K5 | VREF DAC 전압 설정 코드 비트 4 |
| vrc3 | important_control | K5 | VREF DAC 전압 설정 코드 비트 3 |
| vrc2 | important_control | K5 | VREF DAC 전압 설정 코드 비트 2 |
| vrc1 | important_control | K5 | VREF DAC 전압 설정 코드 비트 1 |
| vrc0 | important_control | K5 | VREF DAC 전압 설정 코드 비트 0 |
| t1w2 | important_control | K1 | DFE 탭 1 가중치 제어 코드 비트 2 |
| t1w1 | important_control | K1 | DFE 탭 1 가중치 제어 코드 비트 1 |
| t1w0 | important_control | K1 | DFE 탭 1 가중치 제어 코드 비트 0 |
| t2w1 | important_control | K1 | DFE 탭 2 가중치 제어 코드 비트 1 |
| t2w0 | important_control | K1 | DFE 탭 2 가중치 제어 코드 비트 0 |
| ddl2 | important_control | K6 | DQS 딜레이 라인 튜닝 코드 비트 2 |
| ddl1 | important_control | K6 | DQS 딜레이 라인 튜닝 코드 비트 1 |
| ddl0 | important_control | K6 | DQS 딜레이 라인 튜닝 코드 비트 0 |
| ibias | bias |  | 마스터 기준 전류 바이어스 |
| vdd | power |  | 코어 전원 공급 레일 |
| vddq | power |  | I/O 전원 공급 레일 |
| vss | power |  | 코어 접지 레일 |
| vssq | power |  | I/O 접지 레일 |

## 블록 역할 대응 표 (명세서 §2.6)
| 셀 | 역할 | 확신도 | 기호 | 근거 |
|---|---|---|---|---|
| invx1 | inverter | high | triangle + bubble | 표준 인버터 |
| invx4 | inverter | high | triangle + bubble | 4배 구동 인버터 |
| nand2x1 | nand | high | nand2 gate | 2입력 낸드 게이트 |
| nand2x2 | nand | high | nand2 gate | 2배 구동 낸드 게이트 |
| lvlup | level_shifter | high | box (cell name) | 레벨 시프터 (VDD -> VDDQ) |
| lat_tg | latch | high | box (cell name) | 트랜스미션 게이트 래치 |
| dfftg | flip_flop | high | box (cell name) | TG D-플립플롭 |
| mux2tg | multiplexer | high | mux symbol | 2:1 TG 멀티플렉서 |
| dlybuf | delay_buffer | high | triangle 'BUF' | 딜레이 버퍼 단위 셀 |
| ckbuf | clock_buffer | high | triangle 'CLK' | 클럭 분배 버퍼 |
| padesd | termination_esd | high | R/ESD mark | 입력 보호 ESD 소자 |
| odtleg3 | termination | high | R/switch leg | 3단계 선택 ODT 저항 레그 |
| odtctl | composite | high | box (cell name) | ODT 디코더 컨트롤러 |
| biasgen | bias | high | box (cell name) | 바이어스 전압 생성기 |
| vrefdac | dac | high | box 'VREF DAC' | 64단계 VREF 저항 사다리 DAC |
| dqsamp | cml_buffer | high | triangle 'BUF' | DQS 차동 전치 증폭기 |
| acamp | amplifier | high | triangle 'AMP' | AC 결합 증폭기 |
| dqsrx | composite | high | box (cell name) | DQS 차동 수신기 복합 블록 |
| dqsgate | composite | high | box (cell name) | DQS 게이팅 제어 블록 |
| dly3 | delay_line | high | box 'DLY' | 3비트 디지털 제어 딜레이 라인 |
| sbamp | vga | high | triangle 'VGA' | 단일-차동 변환 프리앰프 |
| sadfe | strongarm | high | triangle + clock | StrongARM 기반 2-탭 DFE 감지 증폭기 |
| srnand | sr_latch | high | box 'SR' | SR NAND 래치 |
| dqslice | composite | high | box (cell name) | 단일 DQ 레인 수신 슬라이스 |
| wldet | phase_detector | high | box 'WL DET' | Write Leveling 위상 검출기 |
| rxbyte_top | composite | high | box (cell name) | 8비트 바이트 수신기 최상위 블록 |
