# 새 시험 세트 (exam)

회귀 세트(`tests/regression/`)와 기준 결과에 나오지 않은 새 시험 netlist 두 개와 채점용 설계 메모다. 시험용 가상 회로다.

| 폴더 | 회로 | 최상위 셀 | 규모 |
|---|---|---|---|
| `rx_s1/` | DQ 수신 1비트 (패드 → 센스앰프 출력, 짝/홀 2위상) | `dq_rx_unit` | MOS 198, 셀 16 |
| `rx_l1/` | 수신 1바이트 (DQ 8개 + DQS/DQSB) | `rxbyte_top` | MOS 1211, 셀 26 |

- `netlist.sp`만 시험 보는 쪽에 준다. `intent.md`(설계 의도, 분류, 함정 목록)는 채점하는 쪽만 본다.
- netlist는 `main` 브랜치의 `hsio-exam/`에도 있고, 시험 브랜치 `test_haiku`, `test_gemini`에는 R0.2 배포 묶음과 `TEST_INSTRUCTIONS.md`(이 폴더의 사본)와 함께 들어 있다.
- 이 폴더는 R0.2 배포 묶음에 들어 있지 않다.
