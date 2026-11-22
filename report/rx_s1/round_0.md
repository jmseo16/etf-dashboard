# rx_s1 — 회차 0 (분류)

## 요약
- 상태: 끝남
- 한 일: netlist 를 손으로 읽어 분류(고속 입력/클럭/출력, 제어 K#, 블록 역할, 질문 5개)를 쓰고, 같은 모델이 검토 역할로 한 번 더 확인해 보완했다. 검토 전/후를 `snapshots/rx_s1/r0_a_classify/`, `r0_c_review/`에 둘 다 저장.
- 못 한 일과 이유: 기준 코드의 `analyze.py` 를 시험 회로에 돌려 보니 깨져서(`classify` 에서 튜플 풀기 오류) 자동 분류는 쓰지 않았다. 분류는 사람이 읽듯이 손으로 했고 자동 분류 도구의 확인은 없다.

## 분류
- 고속 데이터 입력: pad (ESD + ODT), lb_p, lb_n / 고속 클럭 입력: ck, ckb / 고속 출력: dout_e, dout_o / 기준: vref
- 그리는 제어: rtt<2:0> (K4, xi21/mp2.g), odt_en (K4, xi21/mp2.g), tap<3:0> (K1, xi26/mn10.g), tap_sgn (K1, xi26/mn8.g, 낮음), lb_en (K2, xi24/mn6.g), rx_en (K3, xi26/mn2.g, 낮음)
- 숨기는 제어: ofe_p<1:0>, ofe_n<1:0>, ofo_p<1:0>, ofo_n<1:0> (K7 정적 트림, 출처 포트), ibias (K11), net4 (K11)
- 블록 역할 표: `snapshots/rx_s1/r0_c_review/classification.md` 의 표 (esd_dq 종단·ESD, odt_pu 가변 종단, odt_dec DEC 박스, rx_pre 사전에 없음(낮음), ck_gbuf 복합, dfe_sum Σ, sa_dt 비교기(double-tail), sr_nor SR latch, 논리 게이트/LS 는 사전 목록)
- 질문과 가정한 답: Q1 rx_pre 일반 박스 / Q2 rx_en K3 / Q3 tap_sgn K1 / Q4 D=S MOS 커패시터 의도됨 / Q5 오프셋 C 뱅크 가변 C
- netlist 에서 이상하다고 본 곳: rx_pre mn8/mn9 교차 MOS 커패시터, D=S 묶인 MOS 들, sgn/sgnb 이름과 극성 반대(netlist 대로)

## 명세서·묶음에서 막힌 곳
- esd_dq(직렬 R + 양쪽 클램프)를 입력선 위 표시로 그릴 수 없다: 규칙 없음 → 박스로 그림.
- MOS 를 커패시터로 쓴 경우(D=S) 의 그림 규칙이 없다 → 커패시터 기호 + "(MOS C)" 로 표기.
- 기준 전압이 RC 필터를 거쳐 들어올 때 필터를 어떻게 그리는지 규칙이 없다(RC 평균기 사전 행은 있음) → LPF 박스 + 유닛 화면.
- 자동 분류 도구(analyze.py)는 RX AFE 가정(차동 입력 포트, 전원 한 쌍, 다이오드 없음)에 묶여 있어 새 회로에서 바로 쓸 수 없다.

## 걸린 시간·토큰
- 알 수 없음.
