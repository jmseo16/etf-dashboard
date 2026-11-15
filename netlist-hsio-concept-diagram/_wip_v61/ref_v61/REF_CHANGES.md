# 기준 결과 RX AFE — v6.1 개정 기록 (REF_CHANGES)

대상: `reference/rx_afe/`. 기준: `DRAWING_PLAN_v6.md` + `DECISIONS_v61.md`(V1–V27). 옛 상태는 SKILL에 적힌 대로 명세서 v3 결과다.

## 0. 요약

- `bash reference/rx_afe/work/run_all.sh` → `verify_report.json` summary `{'views': 17, 'connectivity_pass': 17, 'quality_pass': 17}`.
- 자동 검사 29개가 모두 pass(건수 0)다. 주입 오류는 57건이며 모두 잡힌다(V25 필수 11종 포함). 결과는 `out/self_checklist.json`에 있다(`auto_checks`, `self_test`).
- 두 번 실행한 결과가 바이트 단위로 같다(scenes.json, out의 JSON·MD). `out/`의 텍스트 4개는 `expected/`와 같다.
- 분류 변경: `G<3:0>` 숨김 일반 제어 → **중요 제어 K6 (버스)**. 나머지 포트·넷의 분류는 그대로다(아래 2절).
- 화면 17개는 그대로다. 그림이 바뀐 화면은 13개(아래 3절)다. 가상 블록 화면 id 5개는 §1.3-1 형식으로 바꿨다.

## 1. 바뀐 파일

| 파일 | 변경 |
|---|---|
| `reference/rx_afe/work/analyze.py` | 추적 간선 기록 → 이득 코드가 여러 비트 경로(같은 셀 형제 인스턴스 2개 이상)에 공유되면 K6. 모든 제어에 `K`, `endpoint`(instance.pin), `source`. 논리 게이트·SR latch·비교기를 사전 행 이름(`nand`/`nor`, `sr_latch`, `comparator`)으로, 확신 높음. 미구동 고속 넷(`undriven_hs`)·미사용 출력(`unused_outputs`) 기록 |
| `reference/rx_afe/work/classify_report.py` | 다시 씀. 질문을 템플릿으로 만들고(`template`·`fields`), 규칙이 정한 것은 묻지 않음(옛 Q5 사전 블록·Q6 미사용 출력·Q7 버스 묶음 삭제, §2.5-7 표기 추측 Q5 추가). 제어 표(K#·끝점 핀·출처·그림), 비고속 분류 점검, 포트 표 K# 열, `annotations._controls`·`_important_control_buses`(K)·`_general_control_buses`·`_not_asked_rule_decided`. **`out/block_dictionary.json`** 생성(§2.6-4) |
| `reference/rx_afe/work/layouts.py` | G 버스(b_top, u_vga), 극성 동그라미·+/−(구조 극성 엔진으로), 버스 사선(비트 수 없음, 이름표·합친 게이트 포트에도), b_slice 탭 입력 왼쪽, b_clk 선 끝 40px, 화면 밖 연결 기호 3화면, SI 값, 가상 블록 id `u_<부모>_<역할>`, 제목 2개, 주석의 Q6 참조, 생략 목록 후처리(버스 한 줄·그린 넷 제외·한국어 분류) |
| `reference/rx_afe/work/scene.py` | `tri`: 출력 동그라미·차동 입력 +/−·출력 핀 이름·위 핀이 있으면 인스턴스 이름 오른쪽·가상 블록 글자 클래스 `vblk`·윤곽선 info. `box`: 출력 동그라미. 핀에 `side`. `offpage()`(화면 밖 연결 기호) 추가. 자리표시자 `fmt_si`(입력 그대로 반환)를 `netlist.fmt_si`로 |
| `reference/rx_afe/work/netlist.py` | 추가만: `fmt_si`, `si_equal`, `group_bus`(`<MSB:LSB>` 묶기와 표기 종류), `Polarity`(구조 극성 엔진: 게이트→부하 드레인 반전, 스택·TG·직렬 R/C 비반전, 하위 블록 포트 극성, 공통모드 노드에서 멈춤) |
| `reference/rx_afe/work/spec_rules.py` | **새 파일**. 명세서에서 온 상수만: 분류 이름(한국어), K 표, 사전 행·사전 목록, 아날로그 역할(V19), 질문 템플릿, 규칙이 정한 주제 |
| `reference/rx_afe/work/verify.py` | 기존 검사는 그대로 두고 넓힘(4절). 기호 획 읽기(SHORT), 이름표 짝·화면 밖 연결 기호, 생략 목록 규칙 전 화면, 4방향 접점·같은 직선 위 선 끝 40px·점선·선 굵기, 화면별 규칙 검사, 전역 검사, `scene_sha`, 주입 시험 57건, `out/self_checklist.json`. 검사·주입이 하나라도 실패하면 종료 코드 1 → `run_all.sh`(set -e)도 실패 |
| `reference/rx_afe/work/render_html.py` | 사이드 패널 분류 요약에 K#와 일반 제어 버스(`C<2:0> (K7)`) |
| `reference/rx_afe/work/make_pptx.py` | 요약 슬라이드 질문 줄 높이를 한글 폭으로 계산(Q3/Q4 겹침 해소) |
| `reference/rx_afe/work/run_all.sh`, `measure.js` | 바꾸지 않음 |
| `reference/rx_afe/work/analysis.json`, `scenes.json`, `texts.json` | 다시 생성(.gitignore 대상) |
| `reference/rx_afe/out/*` | 모두 다시 생성. **새 파일** `self_checklist.json`, `block_dictionary.json`. `screenshots/` 17장(이름 바뀐 5장: `u_top_term`, `u_top_tg`, `u_sa_strongarm`, `u_clk_term`, `u_clk_buf`) |
| `reference/rx_afe/expected/classification.md`, `annotations.json`, `verify_report.json` | 새 분류·새 검증 결과(화면마다 `scene_sha`, `checks`) |
| `reference/rx_afe/expected/block_dictionary.json` | **새 파일** |
| `SKILL_section11_v61.md` | **새 파일**. SKILL §11 교체 문안 + §4.12 예시 + §0·§2.2 줄 + 맞지 않게 남은 SKILL 줄 목록 |
| `REF_CHANGES.md` | 이 파일 |

`rx_afe_top.sp`, `DRAWING_PLAN_v6.md`, `SKILL_v6.md`, `DECISIONS_v61.md`, `.gitignore`는 바꾸지 않았다.

## 2. 분류 변경

### 2.1 포트·넷 분류
| 넷 | 옛 분류 (v3) | 새 분류 | 근거 |
|---|---|---|---|
| G0, G1, G2, G3 → `G<3:0>` | 일반 제어(숨김) | **중요 제어 K6, 버스** | 끝점 = 이득 쌍 꼬리 스위치(VGA 행), VGA 출력 VGA_P/N을 X_DFE_EVEN·X_DFE_ODD가 공유 (§2.5-5 K6, 부록 A, C.8 D6, V1). 끝점 핀 `X_VGA/MS_G0.g`, 출처 최상위 포트 |

다시 점검했지만 바뀌지 않은 것(§2.5 끝점 표, V1–V15):
- `W<4:1>_<3:0>` = K1(V4: 다리 입력이 주 신호와 다른 고속 신호).
- `C<2:0>`, `R<2:0>` = K7 정적 = 일반 제어, 숨김(V7).
- IREF = 바이어스(K11, 미러에만, D5 — ESD 없어 P1 아님).
- VBN/VBP = 바이어스. VCM_RX = 바이어스(V14).
- RX_INP/N 데이터 입력, CLK_INP/N 클럭 입력, DOUT_* 고속 출력, VDD/VSS 전원.
- O_DOUTP/N = 고속 데이터이며 분류 표에 **미구동**(§2.3-13)을 명시.
- V8(mon)·V9(느린 클럭)·V10(슬로우 패드)·V11(검출기 출력)·V12(자기 리셋)·V13(P2)·V15(루프 트림)에 해당하는 넷은 없다. 평탄 넷 중 데이터·클럭 양쪽에서 닿는 넷도 없다.

### 2.2 블록 역할 (`annotations.block_roles`)
| 셀 | 옛 역할 | 새 역할 | 근거 |
|---|---|---|---|
| NAND2 | static_cmos_gate (확신 낮음, "사전에 없음") | **nand** (높음) | §2.6-1 사전 목록(논리 게이트) |
| SR_LATCH | cross_coupled_gates (낮음) | **sr_latch** (높음) | §2.6-1 사전 목록(SR latch) |
| STRONGARM_SLICER | composite (기호 열 "box"인데 그림은 SA 삼각형) | **comparator** (기호 삼각형 "SA" + 클럭) | 비교기 행(StrongARM) 특징 모두 있음 + 출력단 |

### 2.3 질문
| 옛 | 새 | 이유 |
|---|---|---|
| Q1–Q4 | Q1–Q4 (템플릿 `name_vs_structure` ×2, `netlist_error_confirm` ×2) | 내용 같음, 문장은 템플릿 |
| Q5 NAND2/SR_LATCH 사전에 없음 | 삭제 | §2.6-1: 사전에 있음 → 묻지 않음 |
| Q6 미사용 출력 | 삭제 | §3.5-4, §2.7-4 예: 규칙이 정함 |
| Q7 W 16b/4b×4 | 삭제 | §2.5-7: 같은 기능 비트 = 버스 하나 |
| — | **Q5** 비트 표기 추측 (`bus_notation_guess`) | §2.5-7: `_n`·숫자 꼬리 표기 추측 → 확신 낮음 |

## 3. 화면 변경 (scene_sha = 제목·크기·그림 요소(글자 id 제외)·클릭 영역의 SHA-256)

| 옛 id | 새 id | 그림 바뀜 | 옛 scene_sha | 새 scene_sha | 바뀐 내용 |
|---|---|---|---|---|---|
| b_top | b_top | 예 | `fadc9d11f76708edc4044589b3fcd105255fb3d27e49e42f6f3a4d9ec5f409d1` | `ae6d93472091bfa9352e1d006df5490559926ee4680ff3d0efcdad0c5d30533a` | G<3:0> 버스 추가(포트 위 → VGA 위 핀, 사선, X_VGA 이름 오른쪽으로); W 버스 비트 수 "16" 삭제, 아래 슬라이스 W 이름표에 사선(짧은 선 20→30px); CTLE·VGA 입력 +/−(INP "−"), 출력 핀 이름 OUTP/OUTN; CLK_DIST_TREE 박스 CLKI·CLKIB 출력 동그라미; 링크 u_rxterm→u_top_term, u_tg→u_top_tg; 생략 목록(버스 한 줄, 한국어 분류, 블록 문구) |
| b_slice | b_slice | 예 | `cf77f9ede8a1c7badcb765761965d28bc065fb5f1d3fc3fbad2e2e1aebd7b151` | `54c5af376d1e1c30a023a91a59b63d710c98100a67882bdeda8c1cb29d0443c9` | Σ 탭 입력 T1P…T4N을 아래 → 왼쪽 핀으로(V18), 탭 포트에서 곧은 선, Σ 높이 110→270; W 비트 수 "16" 삭제; SA +/−, 출력 핀 이름 QP/QN; X_LATCH1 QP·QN 동그라미; 생략 목록 |
| b_clk | b_clk | 예 | `d7d60b27380da923b583aa2368641627ac43628964c64c173fc5247103c96c24` | `237c3d82b8b4e864796d1d5eb5b476b85e22507938beebbb6f289afc1da985b1` | BUF +/−·B1P/B1N 동그라미·출력 핀 이름, BUF 출력선 끝 380→360(§1.4-7 40px); LATCH 2개 QP·QN 동그라미; BUF 부제 클래스 vblk; 주석에서 Q6 → §3.5-4; 링크 u_clkterm→u_clk_term, u_clkbuf→u_clk_buf; 생략 목록 |
| u_rxterm | u_top_term | 아니오 | `e12b89ba6817cb4962af84c3a4bc6a85642c1d52dee95d71e4ef507666d23d7a` | `e12b89ba6817cb4962af84c3a4bc6a85642c1d52dee95d71e4ef507666d23d7a` | 그림 같음 (id만 u_top_term으로) |
| u_tg | u_top_tg | 예 | `f8003ae673d54357aeb02d1482d7cd28a82d86b1742cf10572a270320ea17b5c` | `61cc336bfd7d9da2c9bec1f591d8d199a34a12b43dbfe317d6cd924d1379e905` | O_DOUTP/O_DOUTN 이름표 → 화면 밖 연결 기호; 주석 "사실상 떠 있음" → "구동원 없음(미구동, §2.3-13, Q3)"; id u_top_tg |
| u_ctle | u_ctle | 예 | `cac551de7e92120a2f94ff6dbcbd21b81270cbb04c5f90223f554f868299ec15` | `cb4a085bc76092fc94840c9dc14fa1e22030293a6c17110236418a9e0810c85d` | 게이트 저항 값 "2000" → "2k"(SI, §3.5-6); 생략 목록(C<2:0>, R<2:0> 한 줄, VDD/VSS 뺌) |
| u_vga | u_vga | 예 | `bf66d823e623d05241797cafa5db45a01e7b6bff9aae7977b8bdb8186edfa125` | `651b18801d5c978eabfbe9c4cde4ceded77a235a104125c4229b827e17a28dd5` | I_G<3:0> 가변 전류원에 G<3:0> 버스 핀·선·사선·포트; 범례 "중요 제어 G<3:0> (K6…)"; 주석; 생략 목록(G 빠짐, VDD/VSS 뺌) |
| u_summer | u_summer | 예 | `838e50d993f344f70e9cef8d458f42839a725f654fc827e0670b76520ad9d42c` | `08288370106dff46cb516432f53ba5df4c7c3aacd9dac93258dfd78b90659c7c` | W 버스 비트 수 "16" 삭제; T<4:1>P/T<4:1>N 버스 포트에 사선; 범례에 K1; 생략 목록(VDD/VSS 뺌) |
| b_sa | b_sa | 예 | `306b9d85627f85c97e04ee2c63f3309523d00669334e6d29cdda08b1a9746e10` | `0456ae1b9b2fbd296e3fa235b10857fd4a07a9dccb82201ca9a43f45602642da` | StrongARM 코어 +/−·OUTP/OUTN 동그라미·출력 핀 이름, 코어 이름 클래스 vblk; SR_LATCH Q·QB 동그라미; 주석에서 Q6 → §3.5-4; 링크 u_strongarm→u_sa_strongarm; 생략 목록 |
| u_strongarm | u_sa_strongarm | 예 | `4b38aa77380af20d726f975fdce16e4b34b44dd5e5fd9b072972469c144151be` | `3d0c3530645c3b63e07c500b390d28d4e5722af922454363499096cafc3ed37c` | OUTP/OUTN 이름표 → 화면 밖 연결 기호; id u_sa_strongarm; 생략 목록(VDD/VSS 뺌 → 비어 있음) |
| b_sr | b_sr | 예 | `88204488fb83e644cace43295359e994a79e82da04ea1ef6c21f0988025a7151` | `5a7148d9473a1865a610f6113087a03320280bc369f0fd63e4f8b188283c285f` | 제목 "(교차 결합 게이트; 사전에 없음 → 박스)" → "(교차 결합 NAND2)"; NAND2 두 개 Y 동그라미; 생략 목록 |
| u_nand | u_nand | 예 | `bb08f01c59ff3d07a5adf01e4bacf5bb12d5c3228edc6f449227b260bcb1978a` | `a954fec43af2d97acf507030a15bde1302ca15762b1a66835e83488ecd39023b` | 제목 "(정적 CMOS 게이트, 사전에 없음 → 소자 그대로)" → "(정적 CMOS NAND)"; 생략 목록(VDD/VSS 뺌) |
| u_inv | u_inv | 아니오 | `95b59c1deb049d2f67339ede368d167ead6ce0df1a1a891be9f8b6c4a9ffabe6` | `95b59c1deb049d2f67339ede368d167ead6ce0df1a1a891be9f8b6c4a9ffabe6` | 그림 같음 (생략 목록만: VDD/VSS 뺌 → 비어 있음) |
| u_latch | u_latch | 아니오 | `07a9669920c5b846dcc2cd8f602cc78329e73b7b78f23197715fa68a02eabf28` | `07a9669920c5b846dcc2cd8f602cc78329e73b7b78f23197715fa68a02eabf28` | 그림 같음 (생략 목록만: VDD/VSS 뺌 → VBN) |
| b_dff | b_dff | 예 | `9e790467e762463615ded29fee352fbd1ccb07c94515cfcc97fc5566bf942add` | `dd05f4068accd11e6c222728493c743ea744a9aa0d8a722f5dc9ad637685a11f` | LATCH 2개 QP·QN 동그라미; 생략 목록 |
| u_clkterm | u_clk_term | 아니오 | `fafb5703aca26abf9b3d4fbbd70d589aa7e2234afc96731a9852e05ed38b8a68` | `fafb5703aca26abf9b3d4fbbd70d589aa7e2234afc96731a9852e05ed38b8a68` | 그림 같음 (id만 u_clk_term으로) |
| u_clkbuf | u_clk_buf | 예 | `d26ff3ec6e2b001c84c214fd86725b9125db98d821ee0f432b64deaaa06fdf94` | `9976b35cd47aec2c74276884e8284a08e94070a6fb1acc2dce0d8893a5073a49` | B1P/B1N 이름표 → 화면 밖 연결 기호; id u_clk_buf; 생략 목록(VDD/VSS 뺌) |

그림이 바뀐 화면은 13개다: b_top, b_slice, b_clk, u_top_tg, u_ctle, u_vga, u_summer, b_sa, u_sa_strongarm, b_sr, u_nand, b_dff, u_clk_buf.
그림이 그대로인 화면은 4개다: u_top_term, u_clk_term(id만 바뀜), u_inv, u_latch(사이드 패널 생략 목록만 바뀜).
사이드 패널의 "분류 요약"과 "가정한 답"은 전체 화면에서 바뀌었다(G<3:0> K6, K#, 질문 Q1–Q5). 이것은 scene_sha에 들어가지 않는 화면 밖 데이터다.

화면이 바뀐 원인별로 묶으면 다음과 같다.
- **분류 변경**(G K6) → b_top, u_vga.
- **v6 버스 표시 §3.5-2**(비트 수 없음, 이름표·합친 게이트에도 사선) → b_top, b_slice, u_summer.
- **극성 §3.4-6/§4.1-13, V19** → b_top(CLK_DIST_TREE 박스), b_slice, b_clk, b_sa, b_sr, b_dff.
- **V21 +/−** → b_top, b_slice, b_clk, b_sa.
- **§3.4-7 출력 핀 이름** → b_top, b_slice, b_clk, b_sa.
- **V18 핀 방향**(Σ 탭 입력) → b_slice.
- **§1.4-7 선 끝 40px** → b_clk.
- **§3.5-1 화면 밖 연결 기호** → u_top_tg, u_sa_strongarm, u_clk_buf.
- **§3.5-6 SI** → u_ctle.
- **§2.6-1 사전 목록**(제목) → b_sr, u_nand.
- **§1.3-1 id** → 링크가 바뀐 b_top, b_clk, b_sa.

## 4. 새 자동 검사와 주입 시험 결과

모든 검사는 화면 17개·모든 핀을 전수 검사한다(V27). 표의 "주입 오류"는 복사본에 오류를 넣고 그 검사의 건수가 늘었는지 본 결과다.

| 검사 | 내용 | 근거 | 기준 결과 | 주입 오류 → 결과 (건수 전→후) |
|---|---|---|---|---|
| 4.1-1 | 연결 재추출 (기하만, 기호 획 포함) | §4.1-1, SKILL §9-1 | pass, 0건 | SHORT — CTLE1_P와 CTLE1_N 사이에 선 [b_top] 0→3 **잡힘**<br>포트 뒤바꿈 — DP ↔ DN [b_dff] 0→2 **잡힘**<br>선 이동 — latch 출력 선 6px [b_clk] 0→3 **잡힘**<br>접점 삭제 [b_slice] 0→1 **잡힘**<br>이름표 바꿈 — E_T2P → E_T3P [b_top] 0→2 **잡힘**<br>기호 획으로 두 핀 잇기 — 열린 스위치 날을 위 접점까지 [b_top] 0→4 **잡힘** |
| 4.1-2 | 보이는 고속 넷 완전성 · 이름표 짝 · 화면 밖 연결 기호 | §4.1-2, §3.5-1 | pass, 0건 | OPEN — 선 끊기 (Σ 출력 → SA 입력 선 삭제) [b_slice] 0→3 **잡힘**<br>경계 넷을 일반 이름표로 (화면 밖 연결 기호 없음) [u_sa_strongarm] 0→1 **잡힘**<br>짝 없는 이름표 — 슬라이스 쪽 O_DOUTP 이름표 삭제 [b_top] 0→3 **잡힘** |
| 4.1-3 | 생략 = 분류 (생략 목록 ↔ 그린 넷, 버스 한 줄) | §4.1-3, §3.5-5 | pass, 0건 | 그리지도 생략하지도 않은 넷 — 생략 목록에서 R<2:0> 삭제 [b_top] 0→3 **잡힘**<br>생략 목록 버스를 비트마다 씀 [b_top] 0→1 **잡힘**<br>그린 넷(VDD 레일)을 생략 목록에 [u_vga] 0→1 **잡힘** |
| 4.1-4 | 기호 = 묶음 | §4.1-4 | pass, 0건 | 소자 삭제 — M1 [u_ctle] 0→1 **잡힘** |
| 4.1-5 | 품질 0 (글씨 겹침, 관통, 대칭, 꼬임, 짧은 꺾임, 접점 근접, 교차, 4방향 접점, 같은 직선 위 선 끝 40px) | §4.1-5, §1.4 | pass, 0건 | 블록 화면 교차 — CLKB 선을 CLK 줄기 위로 [b_slice] 0→1 **잡힘**<br>짧은 꺾임 (<20px) — 탭 입력 선에 10px 꺾임 [b_slice] 0→3 **잡힘**<br>글자 겹침 — X_CTLE1 이름을 CTLE 제목 위로 [b_top] 0→3 **잡힘**<br>4방향 접점 — CLK 줄기 접점에 선 추가 [b_slice] 0→1 **잡힘**<br>같은 직선 위 다른 넷 선 끝 20px (B1P 끝 ↔ B1N 이름표 선) [b_clk] 0→1 **잡힘** |
| 4.1-6 | 떠 있는 포트 | §4.1-6 | pass, 0건 | 떠 있는 포트 — CLKB 포트를 선에서 뗌 [b_slice] 0→1 **잡힘** |
| 4.1-7 | 선 종류 일치 (모두 1.6px 실선, 화면 간 같음) | §4.1-7, §1.4-1 | pass, 0건 | 선 종류 — 선 하나를 2.6px [u_vga] 0→2 **잡힘** |
| 4.1-8 | 합친 블록 범례 | §4.1-8, §3.1-7 | pass, 0건 | 범례 지우기 [u_vga] 0→1 **잡힘** |
| 4.1-9 | 설명 수치 | §4.1-9, §3.5-7 | pass, 0건 | 설명 수치 — 범례 800Ω → 900Ω [u_ctle] 0→1 **잡힘** |
| 4.1-10 | 붙지 않은 출력 핀 | §4.1-10, §3.5-4 | pass, 0건 | 미사용 출력 지우기 — X_CLK.CLKQ 짧은 선+이름표 삭제 [b_top] 0→1 **잡힘** |
| 4.1-11 | 점선 | §4.1-11 | pass, 0건 | 점선 — 선 하나를 점선으로 [b_top] 0→1 **잡힘** |
| 4.1-12 | CCI 배치 | §4.1-12, §3.3-7 | pass, 0건 | n/a — 이 회로에 해당 구조 없음 |
| 4.1-13 | 출력별 극성 (논리 출력만, V19) + 차동 입력 +/− (V21) | §4.1-13, §3.4-6, V19, V21 | pass, 0건 | 동그라미 지우기 — X1(NAND2) 출력 동그라미 [b_sr] 0→1 **잡힘**<br>차동 입력 +/− 뒤바꿈 (V21) [b_top] 0→2 **잡힘**<br>아날로그 출력에 동그라미 (V19) [b_top] 0→1 **잡힘** |
| 4.1-14 | 이름 일치 | §4.1-14 | pass, 0건 | 없는 인스턴스 이름 — X_CTLE1 → X_CTLE9 [b_top] 0→1 **잡힘** |
| 3.5-2-bus_marks | 버스 표시 (사선, <a:b>면 비트 수 없음, <MSB:LSB>) | §3.5-2, §1.4-3, §3.5-1 | pass, 0건 | 버스 이름표의 사선 지우기 (두 번째 슬라이스 W) [b_top] 0→1 **잡힘**<br><a:b> 버스에 비트 수 쓰기 (v3 방식) [b_top] 0→1 **잡힘** |
| 4.1-15 | 핀 이름 (출력 둘 이상·선택 핀) | §4.1-15, §3.4-7 | pass, 0건 | 핀 이름 지우기 — CTLE 출력 OUTP [b_top] 0→1 **잡힘** |
| 4.1-16 | 화면 지문 scene_sha | §4.1-16, §1.2 | pass, 0건 | 화면 주입 41건: 그림 데이터가 바뀐 주입에서만 그 화면의 scene_sha가 바뀌는지 [all] -→- **잡힘** |
| 4.1-17 | 생성 코드 변경 범위 | §4.1-17, §4.3-5 | pass, 0건 | n/a (지문·보고 항목) |
| V24-pin_sides | 핀 방향 (V18 표) | V24, V18, §3.2 | pass, 0건 | 핀 방향 위반 — VGA 이득 코드 핀을 왼쪽으로 [b_top] 0→1 **잡힘** |
| V24-gray_scope | 회색 이름표 허용 범위 | V24, §3.5-3 | pass, 0건 | 회색 이름표 범위 — 블록 화면 VGA 핀에 바이어스 회색 이름표 [b_top] 0→1 **잡힘**<br>회색 이름표 범위 — 보이는 넷(INP)을 회색으로 [u_vga] 0→1 **잡힘** |
| V24-questions | 질문 검사 (확신 낮음 · 템플릿 · 규칙이 정한 것 아님) | V24, §2.7 | pass, 0건 | 질문 검사 — 미사용 출력을 묻기 (규칙이 정함) [global] 0→1 **잡힘**<br>질문 검사 — 확신 높음을 묻기 [global] 0→1 **잡힘**<br>질문 검사 — 템플릿이 아닌 문장 [global] 0→1 **잡힘**<br>질문 검사 — 사전에 있는 NAND2를 사전에 없다고 묻기 [global] 0→1 **잡힘** |
| V24-landing_pins | 끝점 핀 검사 (instance.pin 형식 · 존재 · 넷에서 도달 · 구동원 아님) | V24, §2.5-9 | pass, 0건 | 끝점 핀 — instance.pin 형식 아님 [global] 0→1 **잡힘**<br>끝점 핀 — 없는 인스턴스 [global] 0→1 **잡힘**<br>끝점 핀 — 그 넷에서 도달하지 않는 핀 [global] 0→2 **잡힘**<br>끝점 핀 — 구동원(드레인) 핀 [global] 0→1 **잡힘** |
| V24-cross_table | 표 간 분류 일치 (분류 표 · 포트 표 · annotations · 사이드 패널 · 생략 목록) | V24, V26 M14 | pass, 0건 | 표 간 분류 — annotations 일반 제어에 G0 [global] 0→1 **잡힘**<br>표 간 분류 — classification.md 포트 표 R1을 중요 제어로 [global] 0→1 **잡힘**<br>표 간 분류 — 사이드 패널의 G<3:0> K#를 K7로 [global] 0→4 **잡힘**<br>표 간 분류 — 최상위 생략 목록에서 R<2:0>을 바이어스로 [global] 0→3 **잡힘** |
| V24-block_pins | 블록 핀 이름 = 셀 포트 | V24 | pass, 0건 | 없는 핀 이름 — X_LATCH1 핀 QP → QX [b_slice] 0→1 **잡힘**<br>블록 핀 이름 — 가상 블록 BUF 핀 CLK_INP → INP [b_clk] 0→1 **잡힘** |
| V24-rc_values | R/C 값 = 인스턴스 값 (W/L 포함, SI 표기) | V24, §3.5-6 | pass, 0건 | R 값 — R_IND_P 2k → 3k [u_ctle] 0→1 **잡힘**<br>SI 표기 — R_IND_P 2k → 2000 [u_ctle] 0→1 **잡힘** |
| V24-text_inside | 글자가 박스·화면 밖으로 나감 | V24 | pass, 0건 | 글자가 박스 밖 — NAND2 제목을 박스 밖으로 [b_sr] 0→1 **잡힘**<br>글자가 화면 밖 — 주석을 화면 밖으로 [b_top] 0→1 **잡힘** |
| 2.6-4-block_dictionary | 사전 대응 기록 block_dictionary.json | §2.6-3·4 | pass, 0건 | 사전 대응 — 특징이 빠졌는데 CTLE 기호로 그림 [global] 0→1 **잡힘** |
| M1-files | 파일 · 화면 id · 제목 · 사이드 패널 순서 | M1, §1.2, §1.3 | pass, 0건 | 파일 — block_dictionary.json 없음 [global] 0→1 **잡힘**<br>화면 id — 가상 블록 id가 u_<부모>_<역할>이 아님 [global] 0→2 **잡힘** |
| M10-unit_size | 유닛 화면 기호 20개 이하 | M10, §3.1-8 | pass, 0건 | 유닛 화면 기호 22개 [u_sa_strongarm] 0→1 **잡힘** |

V25 필수 주입 11종이 모두 들어 있다: OPEN, SHORT, 블록 교차, 동그라미 지우기, 미사용 출력 지우기, 없는 핀 이름, 그리지도 생략하지도 않은 넷, 짧은 꺾임(<20px), 글자 겹침, 점선, 핀 방향 위반.
SKILL §9-6의 §4.1-1 예도 모두 들어 있다: 포트 뒤바꿈, 선 삭제, 선 이동, 접점 삭제, 이름표 바꿈, 소자 삭제, 기호 획으로 두 핀 잇기(이 회로에는 선택 스위치가 없어 열린 스위치 날을 반대 접점에 닿게 함).

검사기 자체 확인(기록용, 결과 파일 아님): 같은 검사기를 옛 v3 그림(scenes.json)에 돌리면 다음이 잡힌다.
- G 미표시(visible net not drawn, missing ports).
- Σ 탭 입력 아래 8핀(핀 방향).
- 동그라미·+/−·출력 핀 이름 없음.
- 버스 비트 수 "16", 아래 슬라이스 W 이름표 사선 없음, T<4:1>P/N 사선 없음.
- u_strongarm·u_clkbuf·u_tg 경계 넷에 화면 밖 연결 기호 없음.
- 유닛 화면 생략 목록의 VDD/VSS, 생략 목록 버스를 비트마다 씀.
- "2000"(SI 아님), 가상 블록 id 5개.

## 5. 명세를 이 회로에 적용하면서 애매했던 점 (오케스트레이터 검토 요청)

1. **K5 ↔ K6 (VGA 이득 다리)**. V4는 "코드로 켜는 병렬 다리는 출력이 내부 고속 노드라도 K5"라고 하고, 끝점 표는 위 행이 이긴다(§2.5-3). 그러면 G는 K5다. 부록 A·C.8 D6·V1은 공유 이득 코드를 K6이라 한다. 기준 결과는 K6으로 적고 분류 표에 K5 특징도 맞는다고 적었다. 그림(버스)은 같다. → K6 정의에 "이득 단 다리는 K5보다 K6" 같은 우선순위를 적어야 한다.
2. **"이득 코드"의 구조 정의가 없다(K6)**. CTLE `R<2:0>`·`C<2:0>`도 두 슬라이스가 공유하는 경로의 이득·피킹을 바꾼다. 기준 결과는 사전 행으로 갈랐다: VGA 행의 이득 단 스위치 = 이득 코드 → K6, CTLE degeneration 뱅크 → K7(V7). VGA 행의 "코드로 degeneration R을 바꾸는 차동쌍"이 오면 같은 문제가 생긴다.
3. **부록 A 최상위 포트 줄** "37개 → 9개 (… W 버스 1)"는 같은 표의 G<3:0> K6 행과 맞지 않는다. 지금 결과는 포트 기호 10개(포트 넷 28개), 숨긴 포트 9개다.
4. **V19 "논리 출력"과 §4.1-13 "주 입력"이 정의되지 않았다**. 기준 결과의 해석은 다음과 같다. ① CML latch·StrongARM·클럭 경로 CML 버퍼·논리 게이트·복합 블록(출력을 구동하는 하위 블록을 따름)은 논리 출력이고, CTLE·VGA·Σ는 아날로그다. ② 차동 블록(주 입력 2개, 출력 짝수)은 상보 구동에서 같은 쪽 입력과 비교하고, 그 밖은 첫 입력과 비교한다. 결과로 CML_LATCH(QP=¬DP)·StrongARM 코어·클럭 BUF와 **CLK_DIST_TREE 박스의 CLKI/CLKIB**에 동그라미가 생긴다. 복합 블록·클럭 위상 출력에 극성을 적용할지는 명세가 정해야 한다.
5. **V21의 "+"가 어느 입력인지 정해지지 않았다**. V19가 아날로그 출력의 동그라미를 막으므로, 기준 결과는 "+ = 동그라미 전 첫 출력과 같은 위상인 입력"으로 정했다. 그래서 CTLE·VGA(OUTP가 INP 소자의 드레인 = 반전)는 **위 입력 INP가 "−"**다. 정확하지만 낯설 수 있다.
6. **§2.5-7 "표기 추측 → 확신 낮음"과 §2.7-1의 판단 목록**(고속 입력·클럭·중요 제어·블록 종류)이 겹치지 않는다. 기준 결과는 낮음이면 묻는다(§0.3-3)로 보고 Q5를 넣었다.
7. **§2.6-1 사전 목록 블록**(논리 게이트·SR latch·ICG·DLY·LS·C2C·OTA)에는 구조 특징도 블록도 기호도 없다(C.9-3 일부 미해결). 기준 결과는 박스(셀 이름) + 출력 동그라미로 그렸다. `block_dictionary.json`에는 확인한 구조(NAND: 병렬 PMOS 2 + 직렬 NMOS 2, SR: NAND2 2개 교차 결합)를 적었다.
8. **§1.3-1 "셀 짧은 이름"이 정의되지 않았다**. 가상 블록 id `u_<부모>_<역할>`에 맞춰 u_rxterm→u_top_term, u_tg→u_top_tg, u_strongarm→u_sa_strongarm, u_clkterm→u_clk_term, u_clkbuf→u_clk_buf로 바꿨다(부모 짧은 이름 = 그 부모 블록 화면 id의 꼬리).
9. **§1.4-7 "서로 다른 넷의 선 끝"**. 다른 선 위에서 끝나는(T 접점) 끝과 핀에서 끝나는 끝은 "선 끝"이 아니라고 보았다. 모든 끝을 세면 종단 표시·갈림 모서리의 T 접점 8쌍(20px)이 위반이 된다. 해석을 명세에 적어야 한다.
10. **§3.5-5와 유닛 화면**. "전원 기호로 그린 넷은 뺀다"를 따라 유닛 화면 생략 목록에서 VDD/VSS를 뺐다. 회색 이름표(VBN·VBP)는 "검은 이름표"가 아니라서 남겼다.
11. **scene_sha의 "그림 데이터" 범위**. 제목·크기·그림 요소·클릭 영역만 넣고, 사이드 패널(생략 목록·주석 목록)은 넣지 않았다. 그래서 u_inv·u_latch는 생략 목록이 바뀌어도 sha가 같다.
12. **V18과 DFE 귀환 탭**. 루프 고리 예외는 "루프 화면의 주 경로"(보정 루프 §3.1-6)라서 DFE 귀환에는 적용하지 않았다 → Σ 탭 입력을 왼쪽으로 옮겼다(SKILL §7-2와도 일치).
13. **§3.4-7 삼각형 출력 핀 이름의 자리**가 SKILL §6.4에 없다. 삼각형 안은 제목과 겹쳐서, 출력선 위(위 출력)·아래(아래 출력) 9px 회색으로 두었다.
14. **V24 "R/C 값 = 인스턴스 값"과 개념 기호**. R_S·C_S처럼 여러 소자를 대신하는 기호에는 값 글자가 없다. 범례의 값은 §4.1-9 수치 검사로 확인했다.
15. **CTLE 행 "피킹용 큰 C"의 "큰"**은 양이 정해지지 않았다. 330f(R_S 800Ω와 영점)를 피킹용 C로 보았다.

## 6. 재현

```bash
cd reference/rx_afe && bash work/run_all.sh
for f in classification.md annotations.json verify_report.json block_dictionary.json; do cmp out/$f expected/$f; done
python3 -c "import json;d=json.load(open('out/self_checklist.json'));print(d['self_test'], d['counts'])"
# {'injected': 57, 'caught': 57, 'all_caught': True} {'pass': 20, 'fail': 0, 'na': 7, 'star_fail': 0, 'drawer': 0, 'spec': 0}
```
PPTX는 LibreOffice로 PDF → PNG로 바꿔 요약·b_top·u_vga 슬라이드를 확인했다. 모바일 폭(390px)에서는 17화면 모두 가로 넘침 0이다.
