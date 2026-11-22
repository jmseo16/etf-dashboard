# 분류 확인 표 — DQ_RX_UNIT (rx_s1, 회차 0 검토 전)

```
고속 데이터 입력 : PAD (ESD+종단 붙은 패드, 확신 높음), LB_P/LB_N (루프백 차동쌍, 확신 높음 — Q2로 확인)
클럭 입력        : CK, CKB                  (확신 높음 — 클럭 꼬리 mn0 게이트, ck_gbuf 게이트 경유)
고속 출력        : DOUT_E, DOUT_O           (확신 높음 — SR 래치 → 인버터 버퍼)
중요 제어        : RX_EN (K3, 1줄) / LB_EN (K2, 1줄) / ODT_EN (K4, 1줄) / RTT<2:0> (K4, 버스)
                   / TAP<3:0> (K1, 버스) / TAP_SGN (K2, 1줄)
생략             : 일반 트림 OFE_P/N<1:0>, OFO_P/N<1:0> (K7 포트 출처, 8비트), 바이어스 IBIAS (K11),
                   블록 RX_BIAS (바이어스 발생기), 전원 VDD/VDDQ/VSS/VSSQ, 미사용 출력 2개 (net27, net29)
기준 전압        : VREF (회색 실선, RX_PRE 둘째 입력)
질문             : Q1 RX_PRE 사전에 없음 / Q2 LB_P,LB_N 판정 / Q3 MN8·MN9 (S=D) 의도 / Q4 DFE 루프 복합 블록
```

## 네트 읽기 (구조 근거)

- `esd_dq`(PAD): ESD 다이오드 + 150Ω 직렬 R → `net1` → RX_PRE 입력쌍 게이트.
- `odt_pu`(PAD): PMOS 스위치 + R(60/120/240Ω) → VDDQ. 스위치 게이트 `enb<2:0>`는 `odt_dec`(DEC)의 출력 → K4 종단.
- `rx_pre`: 주 입력쌍(`inp`=PAD, `vref`) + 루프백 입력쌍(`lbp`=LB_P, `lbn`=LB_N). 두 쌍의 꼬리 스위치 `sel_m` = RX_EN & ~LB_EN, `sel_l` = RX_EN & LB_EN → LB_EN은 상보 선택 (K2).
- `dfe_sum` ×2: 주 입력쌍(`inp/inn`) + 판정 피드백 쌍(`hp/hn`, 반대 슬라이스의 SR 래치 Q)이 같은 출력 `outp/outn`에 합산. 꼬리 전류 `tap<3:0>` = 이진 가중(m=8,4,2,1) → K1. `sgn/sgnb`로 피드백 극성 선택 → K2 (TAP_SGN). 꼬리 스위치 `en` = RX_EN → K3.
- `sa_dt` ×2: StrongARM/더블 테일 비교기. 클럭 꼬리 `mn0` 게이트 = CK(게이트된 클럭), 래치 꼬리 `mp2` 게이트 = ~CK. 오프셋 트림 쌍 `ofn/ofp` → 포트 출처 정적 → K7 일반(숨김).
- `sr_nor`×2: 교차결합 NOR SR 래치 (사전 목록). 출력 `q/qb`: 짝수 슬라이스 Q(net14/15) → 홀수 DFE 합산 피드백, 홀수 Q(net16/17) → 짝수 DFE 합산 피드백 (반 속도 DFE 구조).
- `ck_gbuf`: NAND2(ck, en) → INV → CKO, NAND2(ckb, en) → INV → CKOB. 논리 게이트만으로 된 복합 블록(클럭 게이트), `en`=RX_EN.
- `rx_bias`: 미러·다이오드 바이어스 (VBN_Q, IBIAS 생성). 생략.
- `dq_rx_unit.xi9`, `xi12`: 출력 net27, net29 미사용 (짧은 선 + 이름표).

## 블록 역할 (block_dictionary.json 참조)

| 셀 | 역할 | 사전 행 | 확신 |
|---|---|---|---|
| esd_dq | 패드 ESD | 종단 · ESD | 높음 |
| odt_pu | 가변 종단 R | 종단 · ESD (R→전원) | 높음 |
| odt_dec | 디코더 (중요 제어 허브) | 바이어스·DAC·디지털 제어 의 디코더 예외 → DEC 박스 | 높음 |
| ls_lh | 레벨 시프터 | LS (사전 목록) | 높음 |
| rx_pre | 입력 선택 프리앰프 | 사전에 없음 (CTLE 아님: 영점 C 없음, VGA 아님: 이득 코드 없음) | **낮음 → Q1** |
| dfe_sum | DFE 합산 | Summer (DFE·FFE) | 높음 |
| sa_dt | 비교기 (StrongARM/더블 테일) | 비교기·샘플러 | 높음 |
| sr_nor | SR 래치 | SR latch (사전 목록) | 높음 |
| ck_gbuf | 클럭 게이트 | 복합 블록 (NAND·INV 논리 게이트만, 래치 없음 → ICG 아님) | 높음 |
| rx_bias | 바이어스 발생 | 바이어스 → 생략 | 높음 |
| inv_a/inv_c/nand2_a/nand2_c/nor2_c | 논리 게이트 | INV/NAND/NOR | 높음 |

## 질문과 가정한 답 (사용자 없음, 이 답으로 진행)

- **Q1** [block_role, §2.6-3, §2.7-2] `rx_pre` (입력쌍 2개를 sel로 바꾸는 프리앰프): 사전에 없음. (일반 박스 / 사전 행으로)
  - 가정한 답: **일반 박스** "PRE (입력 선택)" + 소자 구성 한 줄 (입력쌍 2, 부하 R 2, 꼬리 2).
- **Q2** [fast_input, §2.4-1] `LB_P, LB_N`: 루프백 차동 입력 쌍(판정 입력 트랜지스터 게이트→데이터 경로). (고속 데이터 입력 / 제어 / 기타)
  - 가정한 답: **고속 데이터 입력(루프백)**. 상대 입력은 PAD.
- **Q3** [netlist_error_confirm, §2.7-4] `rx_pre` MN8, MN9: 게이트=입력(inp/vref), 드레인=소스 단락(MOS 커패시터, 입력→출력). (의도됨 / netlist 오류)
  - 가정한 답: **의도됨**. 박스 안에 "C" 표시만 두고 그리지 않음 (생략 목록).
- **Q4** [block_role, §2.6-복합] DFE 슬라이스 루프: dfe_sum → sa_dt → sr_nor → dfe_sum (피드백은 샘플러 데이터 입력을 거쳐 닫힘). (복합 블록 / 일반 박스)
  - 가정한 답: **복합 블록 "DFE 슬라이스"** (하위 3개 모두 사전 행, 고리는 샘플러 데이터 입력 경유).

## 규칙이 정한 것 (묻지 않음, §2.7-4)

- 사전 목록: INV, NAND2, NOR2, SR latch, 논리 게이트 복합(ck_gbuf), LS → 사전 기호 (§2.6-1).
- 미사용 출력 net27·net29 → 짧은 선 + 이름표 (§3.5-4).
- 버스 묶기: TAP<3:0> (tap<3>..tap<0>), RTT<2:0>, OFE_P<1:0> 등 — 이름 줄기 같고 정수 연속 (§2.5-7). 표기는 `<n>` 그대로라 확신 높음.
- K4 vs K5 (ODT 병렬 다리): 끝점 표에서 K4가 위 → K4로 분류 (그림은 둘 다 버스/1줄로 같음).

## 제어 분류 (§2.5-9)

| 제어 | 비트 | 분류 | K# | 끝점 핀 (인스턴스.핀) | 출처 | 그림 |
|---|---|---|---|---|---|---|
| RX_EN | 1 | 중요 (f) 켜기 | K3 | dfe_sum.xi26/xi27 `mn2.g` (꼬리 직렬 스위치), ck_gbuf `xi0.nand` 입력 | 최상위 포트 (정적) | 1줄 |
| LB_EN | 1 | 중요 (b) 선택 | K2 | rx_pre.sel_m (net102), sel_l (net104) | 최상위 포트 (정적) | 선택 핀까지 1줄 |
| ODT_EN | 1 | 중요 (f) 종단 | K4 | odt_pu (PAD) 스위치 게이트 `enb<k>` (odt_dec 경유) | 최상위 포트 (정적) | 1줄 (DEC 박스 입력) |
| RTT<2:0> | 3 | 중요 (f) 종단 | K4 | odt_pu (PAD) `enb<2:0>` | 최상위 포트 (정적) | 버스 (DEC 입력) |
| TAP<3:0> | 4 | 중요 (a) 가중치 | K1 | dfe_sum ×2 `mn10..mn17.g` (꼬리 가중 쌍) | 최상위 포트 (정적) | 버스 (두 DFE 슬라이스) |
| TAP_SGN | 1 | 중요 (b) 선택 | K2 | dfe_sum ×2 `mn6..mn9.g` (sgn/sgnb 극성 선택) | 최상위 포트 (정적) | 1줄 (두 슬라이스) |
| OFE_P/N<1:0>, OFO_P/N<1:0> | 8 | 일반 (트림) | K7 | sa_dt ×2 `mn7..mn14.g` | 최상위 포트 (정적) | 숨김 |
| IBIAS | 1 | 바이어스 | K11 | rx_bias 다이오드 노드, dfe_sum vbn | 최상위 포트 | 숨김 |

## 비고속 분류 점검

- 기준 전압: **VREF** (ESD 없음, 추적 안 된 넷이 RX_PRE 입력쌍 한쪽 게이트 → 판정 기준) → 회색 실선.
- 상태 출력(O1): 없음. 명령(K8): 없음. 모니터 출력(K9): 없음. 워드 속도 디지털: 없음. 패턴 생성 슬라이스(P2): 없음.

## netlist에서 이상하다고 본 곳

- `rx_pre` MN8, MN9: S=D 단락 MOS 커패시터 (Q3).
- `sa_dt` mn8/mn10/mn12/… : `vss`-`netX`-`vss` 형태 (S=D=vss) MOS 커패시터 — 오프셋 트림 부하로 보임. 그대로 둠.
- `esd_dq` MN0 클램프 게이트가 10kΩ으로 VSSQ에 묶여 항상 꺼져 있음 — 그대로 둠 (ESD 클램프로 표시, 질문 안 함).
- `rx_pre`는 입력 쌍 두 개가 같은 크기(4u/4u)로 사전의 VGA(이득 코드)와 다름 — Q1 근거.
