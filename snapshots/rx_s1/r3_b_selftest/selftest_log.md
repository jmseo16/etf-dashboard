# rx_s1 Round 1 Self-test Log

| 실행 | 검사별 건수 | 총 n건 | 이번에 고친 것 |
|---|---|---|---|
| 실행 1 | conn: 9개 뷰 실패 (b_top, u_pre, u_sa_dt, u_ck_gbuf, u_odt_dec, u_sr_nor, u_ls, u_nor, u_dfe_sum) | 150건+ | 초기 레이아웃 생성 후 자체 검증 실행: 블록 핀 명칭 불일치(net 이름 대신 셀 포트 a, b, y 사용 필요), 버스 슬라이스 LSB/MSB 순서, 개방 선단 검출 |
| 실행 2 | conn: 3개 뷰 실패 (b_top: 23, u_pre: 2, u_sa_dt: 7, 나머지 9개 뷰 통과) | 32건 | u_ck_gbuf, u_odt_dec, u_sr_nor, u_ls, u_nor, u_nand, u_inv 게이트 포트 및 배선 좌표 보정, u_dfe_sum 탭 슬라이스 순서 보정 (9/12 통과) |
| 실행 3 | conn: 2개 뷰 실패 (b_top: 5, u_sa_dt: 2, u_pre: 0 통과) | 7건 | u_pre 루프백 드레인 접점 도트 추가(통과), u_sa_dt mp0/mp1 게이트 플레이트 관통 단락 제거(x=330/730 우회 배선), b_top mn0 핀 수정(G=net3, T/B=vssq) 및 피드백 선 외곽 우회 |
| 실행 4 | conn: 12개 뷰 전체 통과 (0건 실패, connectivity 12/12 PASS) | 0건 | u_sa_dt OFN/OFP 핀에서 배선 분할(pin_on_wire_interior 제거), b_top mn0 vssq 접점 도트 [300, 270] 추가 및 net14~net17 이름표 좌표 배선상 일치 |
| 실행 5 (R2-1) | conn: 12개 뷰 전체 통과 (0건), 4.1-13(극성) 0건 통과 | 0건 | xi22 ODT 디코더 enb<2:0> 반전 출력 버블 추가로 M8 극성 검사 통과 |

## 최종 결과
- **Views Verified**: 12 / 12
- **Connectivity Pass**: 12 / 12 (100% PASS, 0 errors across all views)
- **Quality Checks Run**: V24, V25, V26, M1~M14
