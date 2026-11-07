# HSPICE Netlist → 인터랙티브 스키매틱 스킬: 계획

## 목표
Virtuoso에서 뽑은 HSPICE netlist를 넣으면, 블록 다이어그램에서 트랜지스터 레벨까지
클릭해서 내려가며 볼 수 있는 **단일 HTML 파일**을 만든다. 그림 스타일은 Razavi 교과서풍.

## 확정된 요구사항
| 항목 | 결정 |
|---|---|
| 입력 | Virtuoso HSPICE netlister 출력 형식 (테스트는 Gemini로 만든 netlist 사용) |
| 규모 | 셀당 트랜지스터 수십 개, 계층 깊이 3~5 (유닛마다 다름) |
| 공정 모델명 | 그림에 표시하지 않음 (N/P 구분에만 내부적으로 사용) |
| 블록 정의 | `.subckt`는 블록. top이나 subckt 안에 트랜지스터가 섞여 있으면 **자동으로 묶어서 블록 생성** |
| 트랜지스터 표기 | W, L, M 표시 (뷰어에서 **on/off 토글**) / nf 표시 안 함 / **3-terminal** 심볼 (bulk 생략) |
| 인터랙션 | 보기 전용 (pan/zoom, 클릭해서 계층 이동, 브레드크럼, net 하이라이트, 툴팁). 편집 없음 |
| 출력 | 오프라인에서 열리는 단일 HTML (JS/CSS 모두 inline, CDN 사용 안 함) |
| 스택 | Python (파서, 인식, 검증) + JS (레이아웃 ELK.js, 렌더링 SVG) |
| bias 트랜지스터 | netlist 그대로 트랜지스터로 그림 (전류원 기호로 바꾸지 않음) |
| 블록도 차동 신호 | P/N 두 선으로 그림 (한 선으로 묶지 않음) |

## 파이프라인
```
netlist.sp
 ① parse      → ir.json           (subckt, 인스턴스, 디바이스, net, 파라미터)
 ② group      → ir.json에 자동 블록 추가 (섞여 있는 트랜지스터 묶기)
 ③ recognize  → annotations.json  (블록 타입, 포트 역할, 트랜지스터 그룹)
 ④ layout     → placed.json       (좌표 + 와이어 경로)
 ⑤ render     → schematic.html
 ⑥ verify     → report.json + 스크린샷
```

### ① Parser
- `+` 줄 이어쓰기, `*`/`$` 주석, 대소문자 무시, `.subckt/.ends`, `.param`, `.global`, `.include/.lib`
- Virtuoso 관례: `** Library name / Cell name` 헤더, `mm0`/`xi0`/`rr0` 같은 인스턴스 이름, `m=`, `nf=`, 수식 파라미터
- N/P 판별: 모델명 휴리스틱(`n*`/`p*`, `nch`/`pch` 등). 애매하면 매핑 파일로 지정

### ② 자동 블록 생성 (섞여 있는 트랜지스터)
- **Channel-Connected Component(CCC)**: 전원/접지 net을 빼고 source/drain으로 이어진 트랜지스터끼리 묶음 (디지털/아날로그 회로 분석에서 표준적으로 쓰는 방법)
- 그다음 의미 단위로 합침: 인버터 체인, 차동쌍 + 부하 + tail, 바이어스 미러 등
- 자동 블록 이름은 Claude가 붙임 (예: `auto_diffbuf_0`)

### ③ Recognizer
1. 토폴로지 패턴 매칭(코드): inverter, NAND/NOR, TG, diff pair, current mirror, cascode, cross-coupled pair, 래치, DFF
2. Claude 판단: 패턴 결과 + 이름 + 포트 이름 → 최종 블록 타입과 심볼
3. 사용자 오버라이드 `overrides.yaml`

### ④ Layout
- 블록 레벨: ELK layered, 왼쪽→오른쪽 신호 흐름, 직교 라우팅
- 트랜지스터 레벨: VDD 위 / GND 아래, PMOS 윗행 / NMOS 아랫행, VDD→GND 전류 경로를 세로 열 하나로, 차동 회로는 좌우 대칭
- 인식된 구조는 손으로 다듬은 **배치 템플릿** 적용, 나머지는 규칙 기반 자동 배치

### ⑤ Renderer (Razavi 스타일)
- 흰 배경, 검은 선, 3-terminal MOSFET (화살표로 N/P 구분), 접점 dot, 4방향 접점 금지
- 디바이스 옆에 `W/L ×M`을 작은 글씨로 표시
- 블록 심볼: 버퍼/인버터 삼각형, 차동 버퍼(+/− 입출력), DFF 박스(D, Q, CLK 삼각형), MUX 사다리꼴, 일반 박스

### ⑥ 검증
1. **연결 검증 (필수, 자동)**: SVG의 와이어 기하에서 연결을 다시 뽑아 IR과 디바이스·핀 단위로 비교. 하나라도 다르면 실패
2. **시각 린트 (점수)**: 와이어 교차 수, 심볼 관통, 라벨 겹침, P가 N 위에 있는지, VDD 위/GND 아래, 대칭, 격자 정렬
3. **시각 리뷰**: Playwright로 계층별 스크린샷 → Claude 체크리스트 리뷰 → annotation/힌트 수정 후 다시 그림 → 마지막에 사용자 확인

## 단계
| Phase | 내용 | 완료 기준 |
|---|---|---|
| 1 | Parser + IR + 자동 블록 생성 | 테스트 netlist 전부 파싱, 단위 테스트 통과 |
| 2 | 트랜지스터 레벨 렌더러 + 연결 검증기 | 인버터/CML/5T OTA가 연결 검증 통과 → **스타일을 사용자와 같이 확인** |
| 3 | 블록 심볼 + 블록 레벨 레이아웃 + 드릴다운 | 깊이 3~5 계층형 top이 인터랙티브로 동작 |
| 4 | Recognizer | 테스트셋 분류 정확도 확인 |
| 5 | 시각 검증 루프 | 린트 기준 통과 |
| 6 | 스킬 패키징 (SKILL.md + scripts, eval) | 새 netlist 하나로 처음부터 끝까지 동작 |

## 테스트 코퍼스
- 사용자가 Gemini로 만든 netlist (Virtuoso 형식)
- 보조 golden set: 인버터, NAND2, CML 버퍼, 5T OTA, 2-stage op-amp, StrongARM 래치, TSPC DFF, 링 오실레이터, 그리고 트랜지스터가 섞인 계층형 top

## 그림 규칙
사용자가 준 참고 그림(merged CTLE + DFE summer, CTLE, transceiver 블록도)에서 뽑은 규칙은
`hspice-schematic/references/style_rules.md`에 정리. 핵심: 차동 쌍은 y축 대칭, 입력 쌍 게이트는
바깥쪽 / cross-coupled 쌍은 안쪽 X 배선, degeneration은 R_S 위 C_S 아래, 상위 블록 글씨 겹침 0.

## 진행 상황 (2026-11-07)
- [x] Phase 1 Parser + IR + 자동 블록 생성
- [x] Phase 2 트랜지스터 레벨 렌더러 + 연결 검증기 (스타일 1차 피드백 반영)
- [x] Phase 3 블록 심볼 + 블록 레벨 레이아웃 + 드릴다운
- [x] Phase 4 Recognizer (이름 힌트 + 토폴로지 + overrides)
- [x] Phase 5 시각 검증 (lint: 글씨 겹침, 대칭, 4-way junction, 심볼 관통 / 스크린샷 리뷰)
- [ ] Phase 6 실제 Virtuoso netlist로 검증, skill-creator eval
- 테스트: `python3 -m unittest discover -s tests -v`
- 예시 출력: `examples/*.html`
