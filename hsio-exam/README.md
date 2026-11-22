# HSIO 개념도 스킬 — 시험 netlist

"넷리스트 기반 High-Speed IO 개념도 그리기" 스킬을 여러 LLM으로 시험할 때 쓰는 **새 시험 netlist**다.
지금까지의 회귀 세트(`t1`–`t4`)와 기준 결과(RX AFE)에 나오지 않은 회로이고, 시험용으로 만든 가상 회로다(실제 설계 아님).

| 폴더 | 회로 | 최상위 셀 | 규모 |
|---|---|---|---|
| `rx_s1/` | DQ 수신 1비트: 패드 → ESD·종단 → 프리앰프 → 합산기 → 센스앰프 → SR latch 출력 (짝/홀 2위상) | `dq_rx_unit` | MOS 198, 셀 16 |
| `rx_l1/` | 수신 1바이트: DQ 8개 + DQS/DQSB (스트로브 수신·게이트·지연·클럭 트리, 기준 전압 발생기, 종단 제어) | `rxbyte_top` | MOS 1211, 셀 26 |

- 시험은 브랜치 `test_haiku`, `test_gemini`에서 한다. 두 브랜치에는 R0.2 배포 묶음, 이 netlist 두 개, 시험 지시문 `TEST_INSTRUCTIONS.md`가 똑같이 들어 있다.
- 채점용 설계 메모(`intent.md`)는 시험 보는 쪽이 보지 않도록 여기에 두지 않았다. 스킬 개발 브랜치의 `netlist-hsio-concept-diagram/tests/exam/`에 있다.
