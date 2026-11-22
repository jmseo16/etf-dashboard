# rx_l1 Round 1 Self-test Log

| 실행 | 검사별 건수 | 총 n건 | 이번에 고친 것 |
|---|---|---|---|
| 실행 1 | conn: 16개 뷰 통과, 2개 뷰 실패 (`b_slice`: 40건+, `b_top`: 175건) | 215건+ | 11개 유닛 뷰 및 5개 블록 뷰 초기 통과. `b_slice`에서 탭 가중치 배선이 `net93`/`net94`를 관통하며 거대 단락 형성 확인; `b_top`에서 블록 핀 명칭(`vrc`→`c`, `odtb`→`enb`), `rx_en` 포트 오타 및 미연결 검출 |
| 실행 2 | conn: 17개 뷰 통과, 1개 뷰 실패 (`b_slice`: 0 통과, `b_top`: 104건) | 104건 | `b_slice` 각 가중치 버스선에 독립된 y-jog (55~75) 및 x-트렁크 (340~360) 부여, `net93`(x=320)/`net94`(x=325) 격리 및 (195, 310) 불필요 접점 제거로 **`b_slice` 100% 통과 (err=0)** 달성 |
| 실행 3 | conn: 17개 뷰 통과, 1개 뷰 실패 (`b_top`: 23건) | 23건 | `b_top` `xi0` 인버터 버블(`outb`), 텍스트 박스 크기 확대(`xi8`, `xi1`, `xi12`, `xi13`, `xi38`), 미결합 이름표 및 접점 도트 보정 |
| 실행 4 | conn: 17개 뷰 통과, 1개 뷰 실패 (`b_top`: 17건) | 17건 | `b_top` `xi3.enb`에서 `y=370` 회랑을 통한 `odtb<2:0>` 버스 우회 라우팅으로 `xi2.c<5:0>` 단락 해소, `net212`/`net213` 지연선 레이블 위치 정렬 |
| 실행 5 | conn: 17개 뷰 통과, 1개 뷰 실패 (`b_top`: 6건) | 6건 | `mp0` VDD_SW 레이블 검증 불일치 수정, `xi8.enq` 및 `mp0.B` 선내부 핀 접촉(pin_on_wire_interior) 제거, `xi1`과 `xi0.out` 간 기하학적 접촉 분리 |
| 실행 6 | conn: 18개 뷰 전체 통과 (0건 실패, connectivity 18/18 PASS) | 0건 | `b_top` `net201`을 `y=150` 전용 회랑으로 재배치하여 `ddl<2:0>` 중첩 해소, `net202` 선단 정합, `DQ_SLICES` 상단 `net200` 핀 텍스트 박스 내 수용(`x=880`). **18개 뷰 전원 0 에러 PASS** 달성! |

## 최종 결과
- **Views Verified**: 18 / 18
- **Connectivity Pass**: 18 / 18 (100% PASS, 0 errors across all 18 views)
  - Passing Unit Views (11): `u_invx1`, `u_lvlup`, `u_ckbuf`, `u_padesd`, `u_odtleg3`, `u_sbamp`, `u_dqsamp`, `u_acamp`, `u_srnand`, `u_sadfe`, `u_vrefdac`
  - Passing Block Views (7): `b_odtctl`, `b_wldet`, `b_dly3`, `b_dqsgate`, `b_dqsrx`, `b_slice`, `b_top`
- **Quality & Automated Checks**:
  - `V24-questions`: PASS
  - `V24-landing_pins`: PASS
  - `V24-cross_table`: PASS
  - `2.6-4-block_dictionary`: PASS
  - `M1-files`: PASS
  - `4.1-7-line_kind_views`: PASS
  - `V24-block_pins`: PASS
  - `V24-rc_values`: PASS
  - `V24-text_inside`: PASS (0 fails)
