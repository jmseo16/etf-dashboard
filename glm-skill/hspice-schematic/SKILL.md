---
name: hspice-schematic
description: HSPICE / Virtuoso netlist를 받아 Razavi 교과서 스타일의 인터랙티브 스키매틱(단일 HTML)과 PowerPoint에서 수정 가능한 PPTX를 만들고, 그린 그림이 netlist와 연결이 똑같은지 스스로 검증한다. 사용자가 SPICE/HSPICE netlist(.sp/.cir/.net 또는 .SUBCKT가 들어간 텍스트)를 주며 스키매틱/블록 다이어그램/트랜지스터 레벨 그림을 원할 때 사용.
---

# HSPICE netlist → 인터랙티브 스키매틱 (구현 명세서)

이 문서는 다른 모델(GLM 등)이 **이미 만들어 둔 결과물과 똑같이** 이 도구를 구현하고 사용할 수 있게
쓴 명세서다. 같은 폴더의 `SOURCE_BUNDLE.md`에는 기준 구현의 전체 소스가 들어 있다.

- `SOURCE_BUNDLE.md`를 받았다면: **§0의 방법 A**로 파일을 그대로 풀어서 쓴다 (가장 빠르고 결과가 동일).
- 소스 없이 이 문서만 받았다면: **§0의 방법 B**로 §2~§13을 따라 구현한다. 수치·좌표·색은 모두 그대로 쓴다.
- 어느 쪽이든 마지막에 **§14 검증 절차를 전부 통과**해야 완성이다.

| 파일 | 내용 | 크기 |
|---|---|---|
| `SKILL.md` (이 문서) | 요구사항, 그림 규칙, 알고리즘, 수치·좌표·색, 뷰어 동작, PPTX, 검증, 겪었던 버그, 테스트 netlist | 약 40KB |
| `SOURCE_BUNDLE.md` | 기준 구현 20개 파일 전체 + 복원 스크립트 + 파일별 SHA-256 | 약 240KB |
| `../make_bundle.py` | 기준 구현이 바뀌었을 때 `SOURCE_BUNDLE.md`를 다시 만드는 스크립트 | |

---

## 0. 진행 방법

### 방법 A — 기준 소스 복원 (권장)
1. `SOURCE_BUNDLE.md`의 각 `### FILE: <경로>` 아래 코드 블록 내용을 **한 글자도 바꾸지 말고** 그 경로로 저장한다.
2. `pip install python-pptx` (1.0.x), Node.js + Playwright(Chromium)는 검증용.
3. §14의 명령을 순서대로 실행해 전부 통과하는지 확인한다.

### 방법 B — 명세로부터 구현
§2의 파일 구조대로 모듈을 만들고 §3~§13을 구현한 뒤 §14로 검증한다. 막히면 §15(겪었던 버그)를 먼저 본다.

### 리눅스 설치 (확인된 환경)
- **필수**: Python **3.6 이상** + `python-pptx` (의존: lxml, Pillow, XlsxWriter). 그 외는 표준 라이브러리만 쓴다.
  - 실제로 돌려 본 조합 (전부 단위 테스트 OK, 6개 뷰 PASS, 결과 그림 동일): Python 3.8 + python-pptx 0.6.21 / 0.6.23 / 1.0.2, Python 3.11·3.12·3.13 + python-pptx 1.0.2. 3.6·3.7은 정적 분석(vermin)으로 문법 호환 확인.
  - Python 3.6/3.7(RHEL/CentOS 7 기본)은 python-pptx 0.6.x가 설치된다 (1.0은 3.8 이상). 코드는 둘 다 지원.
- **인터넷이 막힌 서버(오프라인 설치)**: 인터넷 되는 PC에서 대상 서버의 Python 버전에 맞춰 받은 뒤 옮긴다.
  ```bash
  # 인터넷 되는 PC (예: 대상 서버가 Python 3.6, x86_64 리눅스)
  pip download python-pptx -d wheels --python-version 3.6 --only-binary=:all: \
      --platform manylinux2014_x86_64 --implementation cp
  # 대상 서버
  pip install --user --no-index --find-links wheels python-pptx
  python3 -c "import pptx; print(pptx.__version__)"
  ```
  (3.6용으로 받으면 python_pptx-0.6.23, lxml-5.4.0, Pillow-8.4.0, XlsxWriter-3.2.2가 받아진다.)
- **결과 보기**: HTML은 리눅스의 Firefox/Chrome으로 바로 열린다(인터넷 불필요). PPTX는 LibreOffice Impress로 열리고, 윈도우 PowerPoint에서 수정한다.
- **선택(검증 도구)**: `screenshot.js`, `ui_selftest.js`는 Node.js 18+ 와 Playwright(Chromium)가 필요하다. 서버에 없으면 이 두 단계만 건너뛰고, 빌드 콘솔의 `CONNECTIVITY: ALL VIEWS MATCH NETLIST`, lint 0, `python3 -m unittest discover -s tests`로 검증한다. PPTX를 그림으로 확인하려면 `soffice`(LibreOffice)와 `pdftoppm`(poppler-utils).

### 사용 (구현이 끝난 뒤 매번)
```bash
python3 scripts/build.py NETLIST.sp -o OUT.html --report OUT_report.json   # OUT.html + OUT.pptx 생성
node scripts/screenshot.js OUT.html shots/          # 계층별 PNG (눈으로 확인)
node scripts/ui_selftest.js OUT.html                # 모든 버튼 자동 점검 → "0 failed"
```
1. 콘솔에 `CONNECTIVITY: ALL VIEWS MATCH NETLIST`가 나와야 한다. 하나라도 `[FAIL]`이면 전달하지 않는다.
2. 각 뷰의 lint 경고는 0이어야 한다 (글씨 겹침, 대칭, 접점 등).
3. 스크린샷을 눈으로 보고 §1의 그림 규칙을 확인한다.
4. 블록 인식이 틀렸으면 `--annotations ann.json`으로 고친다 (§5.5).
5. 사용자에게 HTML과 PPTX를 주고, 계층 구조·인식된 블록(근거)·자동 생성 블록·검증 결과를 요약한다.

---

## 1. 확정된 요구사항 (사용자와 합의된 것 — 바꾸지 말 것)

| 항목 | 결정 |
|---|---|
| 입력 | Virtuoso가 뽑은 HSPICE netlist. 셀당 트랜지스터 수십 개, 계층 깊이 3~5 |
| 출력 | ① 오프라인에서 열리는 **단일 HTML** (JS/CSS 전부 inline, CDN 금지) ② **PPTX** (PowerPoint에서 수정 가능) |
| 상호작용 | **보기 전용**. 웹에서 편집하는 기능은 만들지 않는다 |
| 계층 | 블록 클릭 → 하위 계층, 경로(breadcrumb), Esc/↑상위로 복귀 |
| 블록 정의 | `.subckt` = 블록. 셀 안에 트랜지스터와 subckt가 섞여 있으면 **자동으로 블록을 만든다** |
| 트랜지스터 표기 | W/L, m 표시 (뷰어에서 on/off 토글). **nf는 표시하지 않음**. **3-terminal** 심볼(bulk 생략). **공정 모델명은 그림에 쓰지 않음** |
| 토글 | W/L·m, R/C 값, 소자 이름, 넷 이름(기본 꺼짐) |
| bias 트랜지스터 | netlist 그대로 트랜지스터로 그림 (전류원 기호로 바꾸지 않음) |
| 블록도 차동 신호 | P/N 두 선으로 그림 (한 선으로 묶지 않음) |
| 포트 | 모든 계층에서 **Virtuoso 스키매틱 핀** 모양 (빨간 오각형/육각형) |
| 그림 스타일 | Razavi 교과서 스타일 (아래 그림 규칙) |
| 화면 문구 | 툴바/사이드 패널의 고정 문구는 한글, 회로 관련 텍스트(인식 근거, 검증 메시지, 블록 종류 이름)는 영어. **이 상태 그대로 둔다** |
| 모바일 | 폰에서도 동작 (한 손가락 이동, 두 손가락 확대/축소, 탭) |

### 그림 규칙 (사용자가 준 참고 그림: merged CTLE+DFE summer 논문 그림, CTLE 그림, transceiver 블록도)
1. **y축 대칭**: 차동 쌍(INP/INN, OUTP/OUTN, SP/SN … 로 매칭되는 같은 크기 소자)은 세로축 기준 거울상으로 그린다. 셀 전체가 대칭이면 축 하나(CTLE, CML latch), 아니면 쌍마다 자기 tail 기준(merged summer: main 쌍과 tap 쌍이 나란히).
2. 같은 노드에 매달린 같은 크기 형제(클럭 쌍 등)도 부모 기준 거울 배치.
3. 게이트 방향: 입력 쌍은 **바깥쪽**(IN은 왼쪽, IN̄은 오른쪽), cross-coupled 쌍과 게이트를 공유하는 쌍은 **안쪽**. cross-coupled 게이트 배선은 축 위에서 **대각선 X**.
4. 위→아래: VDD 레일, 부하, 트랜지스터, tail, 접지. PMOS는 NMOS 위. 부하는 드레인 바로 위, tail은 자기가 먹이는 쌍의 가운데 아래.
5. drain/source 노드는 **가로선 한 줄** + 세로 연결. 같은 높이에서 겹치면 두 번째는 한 칸(20px) 위/아래 트랙.
6. degeneration: 두 소스 노드 사이 수동소자는 가로로, **R_S 위 C_S 아래**, 소스 세로선에 직접 붙어 접점 점 4개.
7. MOSFET 심볼: 굵은 채널이 drain/source 꺾임 끝에서 정확히 끝남, 게이트판과 채널 사이에 뚜렷한 gate oxide 간격(9px), 몸통 21×30px, 소스 꺾임에 화살표(NMOS 바깥쪽, PMOS 안쪽).
8. VDD는 위쪽 가로 레일 하나, 접지는 가지마다 개별 접지 기호.
9. 포트 = Virtuoso 핀: 입력 = 회로 쪽을 가리키는 오각형, 출력 = 바깥을 가리키는 오각형, 입출력 = 육각형. 빨간색.
10. T 접점에는 점, 4방향 접점 금지, 교차는 점 없이.
11. 소자 이름·W/L·m은 게이트 반대편 옆에.
12. 블록도: 신호는 왼쪽→오른쪽, 입력에 화살촉, feedback 입력은 블록 아래로, 클럭은 아래에서, bias는 블록 위 짧은 선 + 핀/이름.
13. 블록 심볼: CTLE/증폭기 = 삼각형(+/− 표시), summer = Σ 원, latch/DFF = 박스(DFF 클럭 ▷ 표시), NAND/NOR 등 = 게이트 모양, 그 외 = 셀 이름 박스.
14. **어떤 글씨도 다른 글씨·배선·심볼과 겹치지 않는다** (특히 상위 블록도).

---

## 2. 구조

```
hspice-schematic/
  scripts/build.py            CLI (파싱→분석→배치→배선→렌더→검증→PPTX→재렌더)
  scripts/hsch/parser.py      netlist → IR
  scripts/hsch/analyze.py     전원/접지, 포트 역할, 자동 블록, flatten, 블록 인식
  scripts/hsch/geom.py        심볼 라이브러리 (좌표는 §9)
  scripts/hsch/router.py      격자 미로 배선기 (§7)
  scripts/hsch/layout_leaf.py 트랜지스터 레벨 배치 + 배선 (§6, §7)
  scripts/hsch/layout_block.py 블록 레벨 배치 + 배선 (§8)
  scripts/hsch/render.py      scene → 단일 HTML (§10)
  scripts/hsch/verify.py      그림에서 연결 재추출 + lint (§13)
  scripts/hsch/export_pptx.py scene → PPTX (§12)
  scripts/screenshot.js       계층별 PNG
  scripts/ui_selftest.js      뷰어 버튼 전체 자동 점검 (§14)
  assets/viewer.css, viewer.js  뷰어 (§10, §11)
  references/style_rules.md   그림 규칙
tests/test_hsch.py            단위/통합 테스트
tests/netlists/*.sp           테스트 netlist (부록)
```

파이프라인 (build.py):
1. 파싱 → IR0. `--annotations`의 `mos_types` 적용.
2. `extract_auto_blocks(IR0)` → IR. **flatten(IR0) == flatten(IR)** 를 assert (자동 블록이 연결을 바꾸지 않음).
3. `port_roles(IR)`, `classify_all(IR, annotations)`.
4. top에서 도달 가능한 셀 순서(DFS, 그다음 다른 root) → 셀마다 scene: subckt 인스턴스가 있으면 `layout_block`, 없으면 `layout_leaf`.
5. viewer용 info(JSON) 구성 → HTML 렌더 → `verify_html`로 HTML을 다시 읽어 검증 → 검증 결과를 info에 넣고 PPTX 생성 → PPTX를 base64로 포함해 HTML 재렌더 (그림은 동일).
6. 콘솔: 뷰별 `[PASS]/[FAIL]`, 교차 수, lint 수, 셀별 인식 결과. 종료코드 0 = 모두 PASS.

CLI: `build.py NETLIST [-o out.html] [--annotations ann.json] [--top CELL] [--ir-json ir.json] [--report report.json] [--pptx out.pptx]` (pptx 기본값: HTML 옆 같은 이름 `.pptx`).

---

## 3. 파서

- 줄 처리: 빈 줄과 `*`로 시작하는 줄은 주석. `$`는 줄 맨 앞이거나 앞이 공백일 때 이후 주석. `+`로 시작하는 줄은 앞 줄에 이어 붙임.
- 토큰: 먼저 `\s*=\s*` → `=`. 따옴표 `'…'`/`"…"` 안은 한 토큰. 구분자는 공백·탭·`,`·`(`·`)`.
- `key=value` 토큰은 params(키 소문자), 나머지는 위치 토큰.
- 대소문자 무시: 셀마다 처음 나온 철자를 대표 이름으로 쓴다 (`.global` 넷은 전역).
- dot 카드: `.subckt/.macro name ports… [k=v]` (`params:` 토큰 무시), `.ends/.eom`, `.param`(셀 또는 전역), `.global`, `.model name type`(nmos/pmos 판별용), `.include/.inc/.lib file`(파일이 있으면 그 자리에 펼침, 깊이 ≤ 8, 없으면 경고). 나머지(.option/.end/.temp …)는 무시.
- 소자:
  - `M d g s b model params` (pins d,g,s,b)
  - `R/C/L n1 n2 [value | model [value]] params` (pins p,n; 값은 r/c/l 키)
  - `V/I p n …`(나머지는 value), `E/G p n cp cn [gain]`, `F/H p n vctrl`, `D a k [model]`, `Q c b e [model]`
  - `X nodes… subname params` (subname = 마지막 위치 토큰)
- MOS 타입: annotations `mos_types` → `.model` 타입 → PMOS 힌트 `(^p|pch|pmos|pfet|_p\b)` → NMOS 힌트 `(^n|nch|nmos|nfet|_n\b)` → 모르면 nmos + 경고.
- 파싱 후 X 핀을 subckt 포트 이름으로 매핑(subckt 이름 대소문자 무시). 개수 불일치·미정의 subckt는 경고(미정의면 핀 이름 p1…pn).
- top: subckt 밖에 소자가 있으면 가상 셀 `__TOP__`. 아니면 다른 셀이 인스턴스하지 않는 root 중 계층이 가장 깊은 것(동률이면 소자 많은 것).
- 숫자: `^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)(meg|mil|[tgxkmunpfa])?[a-z]*$` (대소문자 무시). T=1e12 G=1e9 MEG=X=1e6 K=1e3 MIL=25.4e-6 M=1e-3 U=1e-6 N=1e-9 P=1e-12 F=1e-15 A=1e-18. 뒤 단위 글자(`fF`, `um`)는 무시.

### IR (JSON)
```json
{"top": "CELL", "roots": ["CELL"], "globals": [], "params": {}, "warnings": [],
 "cells": {"CELL": {"name": "CELL", "ports": ["A", "B"], "params": {},
   "auto": false, "parent": null,
   "devices": [{"name": "M1", "kind": "M", "type": "nmos",
                "pins": [["d","OUTP"],["g","INP"],["s","SP"],["b","VSS"]],
                "model": "NCH", "params": {"w": "16u", "l": "45n"}, "ref": null, "line": 4}]}}}
```
type: nmos/pmos/res/cap/ind/vsrc/isrc/vcvs/vccs/cccs/ccvs/diode/bjt/inst. 자동 블록 인스턴스는 `"auto": true`.

---

## 4. 표기 형식
- 공학 표기 `eng(v)`: T G M k (없음) m µ n p f a 중 `|v| ≥ scale×0.9995`인 가장 큰 접미사, 유효숫자 3자리(`%.3g`), 예 16e-6→`16µ`, 45e-9→`45n`, 1000→`1k`.
- MOS: `W/L` = `16µ/45n`, 다음 줄 `m=1` (params의 m 또는 mult, 없으면 1). nf는 표시 안 함.
- R `600Ω`, C `150fF`, L `…H`.

---

## 5. 분석 (analyze.py)

### 5.1 전원/접지, 클럭, bias 이름
- 전원: `^(a|d)?(vdd|vcc|vpwr|vdda|vddd|vddh|vddl)\w*$`, 접지: `^((a|d)?(vss|gnd|vgnd|vssa|vssd)\w*|0)$` (대소문자 무시).
- 클럭: `(^|_)(clk|ck|clock|phi|ph)\w*$|^(clk|ck)`, bias: `^(vb|vbias|bias|vref|ibias|iref|vcm|vbn|vbp)|bias`.
- 차동 짝 이름: `^(.*?)(_?)(p|n|plus|minus|\+|-)$` → 접미사를 바꾼 이름이 존재하면 짝 (p/plus/+ = "+", n/minus/- = "−").

### 5.2 포트 역할 (재귀, 메모)
셀의 각 포트가 연결된 곳을 모은다: MOS d/s→`ds`, MOS g→`g`, MOS b→`b`, X→하위 셀 포트 역할 `sub:<role>`, V/E/G/F/H의 p/n→`drv`, 그 외→`pass`.
- 이름이 전원/접지면 power/ground.
- `ds` 또는 `drv` 또는 하위 `out` 있으면 **out**.
- 아니고 `g` 또는 하위 in/clk/bias 있으면 **in** (하위가 전부 clk이고 g 없으면 clk, 전부 bias면 bias).
- 아니고 하위 power/ground면 그 역할, 아니면 inout.
- in인데 이름이 bias 패턴이면 **bias**, 클럭 패턴이면 **clk**.

### 5.3 자동 블록 (트랜지스터와 subckt가 섞인 셀)
1. 셀에 X도 있고 primitive(M R C L V I E G F H D Q)도 있으면 실행.
2. primitive끼리 union-find: 전원/접지가 아닌 **채널 넷**을 공유하면 같은 그룹 (MOS는 d,s / E,G는 p,n / 나머지는 모든 핀). 게이트만 공유하는 건 묶지 않음.
3. 그룹을 첫 소자 줄 번호 순으로. **R/C/L 하나뿐인 그룹은 묶지 않고 그대로 둔다**(블록도에 소자 그대로 그림).
4. 나머지 그룹 k → 새 셀 `<셀>__AUTO<k>`(auto=true, parent=셀), 인스턴스 `XAUTO<k>`(auto=true). 포트 = 그룹 넷 중 (부모 포트 ∪ 전원/접지 ∪ 그룹 밖 소자가 쓰는 넷), 순서는 부모 포트 순서 → 등장 순서. 인스턴스 핀 이름 = 넷 이름.
5. flatten: 소자 경로 이름(자동 블록은 경로에 안 들어감) → 핀별 평탄화 넷. 변환 전후 결과가 같아야 한다.

### 5.4 블록 인식
**이름 힌트** (자동 블록이 아닐 때만, 순서대로 첫 일치): nand, xor, `(^|_)nor\d*($|_)`→nor, `(^|_)and\d*($|_)`→and, `(^|_)or\d*($|_)`→or, `ctle|equali[sz]`→ctle, latch, `dff|flop|(^|_)ff(_|$)`→dff, sum→summer, dfe, mux, inv→inverter, `buf|drv|driver`→buffer, `ota|opamp|amp`→amplifier, comp→comparator.

**구조 특징** (primitive만 있는 셀):
- diff pair: 같은 타입 MOS 두 개, 소스 공유(비전원), 드레인 다름, 게이트 다름 (게이트가 둘 다 클럭이면 clock pair).
- cross-coupled: 소스 공유 + A.g=B.d, B.g=A.d.
- degeneration: 같은 W/L, 소스가 서로 다른 비전원 넷, 그 두 소스 사이 R 또는 C.
- res_loads: 한쪽이 전원인 R. inverter: 게이트·드레인 공유, NMOS 소스 접지, PMOS 소스 전원.

**구조 규칙** (순서): cross-coupled 있고 clock pair 또는 diff pair 있으면 **latch** → degeneration 있고 diff pair 없고 저항 부하 있으면 **ctle** → diff pair 2개 이상이 같은 드레인 쌍으로 모이면 **summer** → NAND/NOR(한쪽 망 병렬, 다른 쪽 직렬, 게이트 집합 동일) → diff pair 있으면 **diff_buffer** → inverter 1개면 inverter, 여러 개면 buffer. subckt만 있는 셀: 인스턴스 2개가 모두 latch면 **dff**.
이름 힌트가 있으면 이름이 우선(구조가 다르면 근거에 `(topology suggests X)` 추가). 근거 문자열 예: `name 'CML_LATCH'; cross-coupled pair + steering pairs`, 없으면 `no pattern`.

**클래스 → 심볼/제목/라벨**

| class | shape | 심볼 안 제목 | 라벨 |
|---|---|---|---|
| ctle | amp | CTLE | CTLE |
| buffer / diff_buffer / amplifier | amp | (없음) | Buffer / Diff. buffer / Amplifier |
| comparator | amp | CMP | Comparator |
| inverter | inv | | Inverter |
| summer | sum | (Σ) | Summer |
| latch | latch(박스) | LATCH | Latch |
| dff | dff(박스) | DFF | D flip-flop |
| mux | mux | MUX | MUX |
| dfe | box | DFE | DFE |
| nand/and/nor/or/xor | 게이트 | | NAND … |
| generic | box | 셀 이름 | Block |

자동 블록 셀의 화면 표시 이름은 `<라벨> (auto)` (예 `Summer (auto)`), 블록도에서 인스턴스 라벨은 `(auto) : Summer`. 일반 셀은 셀 이름, 인스턴스 라벨은 `X_DFE : DFE_1TAP`.

### 5.5 annotations.json
```json
{"cells": {"MY_SLICER": {"class": "latch"}, "TOP__AUTO0": {"class": "summer", "label": "Summer"}},
 "mos_types": {"nch_lvt_mac": "nmos", "pch_hvt_mac": "pmos"}}
```
class만 주면 shape/title은 표에서 채운다.

---

## 6. 트랜지스터 레벨 배치 (layout_leaf)

상수: 격자 G=10, **RP=120**(넷 랭크 간 세로 간격), **GAP=20**(열 사이 최소 간격), **HGAP=110**(가로 수동소자를 넣을 간격), CHAR=5.6(글자 폭 추정).

1. **레일**: 전원 = 포트 중 전원 이름 첫 번째(없으면 넷 중), 접지도 같은 방식.
2. **방향**: 세로 소자의 (아래 넷, 위 넷): NMOS (s,d), PMOS (d,s). 위가 접지거나 아래가 전원이면 뒤집음(이때 심볼 핀 이름 d↔s 교체). Q (e,c), D (k,a). R/C/L/V/I는 한쪽이 접지/전원이면 그쪽이 아래/위, 둘 다 내부 넷이면 랭크 계산 뒤 결정. 그 외(E,G…)는 오른쪽에 generic 박스.
3. **랭크**: 접지 = 0. 세로 소자마다 h(위) ≥ h(아래)+1을 최장경로로 반복 완화(전원/접지는 위로 올리지 않음). top = max(전원으로 가는 h(아래)+1, max(h)+1). 전원 = top. 전원에서만 닿는 넷은 h(아래) = h(위)−1로 채움. 접지 아닌 넷의 최소 랭크가 1보다 작으면 전체를 올림.
4. 내부 넷 사이 수동소자: 두 넷 랭크가 다르면 세로(낮은 쪽이 아래), 같으면 **가로**.
5. **대칭 σ** (차동 거울):
   - 시작: 전원/접지는 자기 자신, 이름 짝(5.1)은 서로.
   - 반복: 아직 짝 없는 소자 d에 대해 같은 (kind, type, w/l/m/nf/r/c)인 후보 e(자기 자신 포함)를 찾아, 핀별로 σ(넷_d) = 넷_e가 기존 σ와 모순 없으면 후보(R/C/L은 핀 뒤바꿈도 허용, MOS bulk 제외).
   - 새로 추정해야 하는 넷 수가 가장 적은 후보가 유일하게 최선이면 채택(동점이면 자기 자신 아닌 쪽 우선, 그래도 동점이면 보류). 진전이 없을 때까지.
6. **트리**: 전원에 붙은 채널 소자 수(sc)가 0 < sc < 접지에 붙은 수(gc)이면 위에서 아래로(PMOS 입력단 등), 아니면 아래(접지)에서 위로 자란다. 넷 → 그 넷에 "올라탄" 소자들(아래에서 위로면 아래 넷이 그 넷인 소자). 자식 정렬은 netlist 순서, σ 짝은 바로 옆에. 각 소자의 다른 쪽 넷이 아직 방문 안 했고 레일이 아니면 재귀로 확장. 남은 소자는 (랭크, 순서)로 새 루트. DFS 순서 = 왼→오 순서(order). band = 위 넷의 랭크.
7. **쌍 만들기**: σ 쌍(같은 band) + **같은 비전원 노드의 자식 중 같은 kind/type/크기인 형제**(클럭 쌍 M5/M6 등). 왼쪽 = order가 작은 쪽.
8. **전역 대칭 모드** 조건: 쌍에 못 든 소자는 모두 σ 자기대칭이고 band마다 1개 이하, 가로 수동소자도 모두 σ 자기대칭, 쌍이 1개 이상, generic 소자 없음. (CTLE, CML latch는 전역 대칭 / merged summer는 MB_M·MB_T1 두 개가 같은 band → 트리 모드.)
9. **게이트 방향**(mirror=게이트가 오른쪽): 쌍 (a 왼, b 오) — inward(게이트 공유 또는 cross-coupled)면 a mirror, b 그대로 / 아니면 a 그대로, b mirror. 트리 모드에서 쌍이 아닌 같은 band의 이웃 MOS가 게이트를 공유하면 왼쪽 mirror(전류 미러처럼 마주 봄).
10. **폭(extent)**: MOS 게이트 쪽 = 40 + (게이트 넷이 핀 하나뿐이면 ceil10(len(이름)×5.6+14+20) 아니면 10), 라벨 쪽 = max(ceil10(label_w), 20) (label_w = max(len(name), len(W/L), len(m))×5.6+8). mirror면 좌우 바꿈. 그 외 소자 (20, max(ceil10(label_w),20)).
11. **x 배치 — 전역 대칭 모드**:
    - inner_score(왼쪽 대표): inward 쌍 +2, 게이트가 핀 하나뿐인 입력 −1, 나머지 0 (수동소자 0).
    - 열(column): σ(넷)≠넷 인 노드에서 위에 탄 왼쪽 대표들 중 inner_score 최소와 아래쪽 중 최소를 같은 열로 합침(같은 band가 겹치면 안 합침). σ 자기대칭 노드(tail)는 열을 잇지 않는다.
    - 열 정렬: (−max inner_score, 최소 order) → 안쪽부터.
    - band별 축 여유 half: 축 위 소자가 있으면 max(lext,rext)+GAP, 가로 수동소자가 있는 랭크 r에서는 band r, r+1에 HGAP/2.
    - 열마다 x = min over 열의 각 소자 [ 같은 band 직전 소자가 있으면 prev.x − prev.lext − GAP − rext, 없으면 −max(half, GAP/2) − rext ], 10 단위로 내림. 짝은 −x, 축 소자는 0.
12. **x 배치 — 트리 모드**: 잎은 (−lext, rext), 자식들을 왼→오로 간격 GAP(+HGAP: 왼쪽 묶음과 오른쪽 자식 사이에 가로 수동소자가 걸치면)으로 붙이고, 부모 x = 첫·끝 자식의 가운데(10 단위 반올림). 부모 윤곽은 자식들 + 자기 폭. 루트들도 같은 방식으로 나란히.
13. **y**: y(r) = (top − r)×RP. 소자 중심 = y(위 넷 랭크) + 60 → 핀은 중심 ±30.
14. **가로 수동소자**: 두 넷의 기준 x(그 넷에 닿는 세로 소자 x 평균)의 가운데. 같은 두 넷 사이 k번째는 y = y(랭크) + [−10, +20, −40, +50][k]. p핀이 왼쪽 넷이면 rot=3, 아니면 rot=1. 라벨 `이름 값`은 k 짝수면 위(y−12), 홀수면 아래(y+21), 가운데 정렬.

---

## 7. 배선 (router.py + layout_leaf의 순서)

### 7.1 격자 미로 배선기 (A*)
- 격자 10px. 상태 = (칸, 진행방향). 비용: 한 칸 1, 꺾임 +6, 다른 넷과 교차 +14, 다른 넷 핀 바로 앞 칸 +12, soft 영역 비용(라벨 25 등) 더함. 탐색 한도 60000.
- **규칙**: 다른 넷 선과 같은 방향으로 겹침 금지 / 교차는 수직으로 곧게 지나갈 때만(그 칸에서 꺾기·끝나기·접점 금지) / 다른 넷의 핀·접점·꺾임 칸 진입 금지 / 심볼 keepout 진입 금지 / 핀에서는 핀 방향으로 출발, 핀에는 반대 방향으로 도착 / 4방향 접점 금지(도착 칸 차수 ≤ 2일 때만 T 허용) / 이미 교차가 있는 칸은 세 번째 넷 통과 금지.
- 다핀 넷: 첫 핀(중심에 가장 가까운 핀)을 트리로 두고, 트리에 가장 가까운 핀부터 A*로 트리 아무 칸에 연결. 실패한 핀은 이름표로 연결(경고).
- `try_fixed(net, polylines)`: 미리 정한 선을 위 규칙(겹침·교차·4방향·남의 핀/노드) 검사 후 통과할 때만 확정.
- 출력: 같은 방향 연속 칸을 최대 직선으로 합침, 차수 ≥3 칸(핀은 리드 1 포함)에 접점 점.

### 7.2 트랜지스터 뷰 배선 순서
1. 라우터 범위 = 심볼 bbox ±120/±100. 모든 keepout은 hard, 소자 라벨 영역은 soft 25, 핀 등록(MOS bulk 제외).
2. **접지**: 각 접지 핀에서 핀 방향으로 10px 선 + 접지 기호(그 아래 칸 막음).
3. **VDD 레일**: 위를 향한 VDD 핀들의 x 범위 −30~+30, y = y(top). VDD가 포트면 레일 왼쪽 끝에 **입출력 핀**, 아니면 레일 가운데 위에 이름. VDD 핀들을 레일로 배선, 실패하면 국소 VDD 기호.
4. **노드 버스**: 세로 소자의 위/아래 핀(U/D)만 모아서, 그 넷의 랭크 y에 트랙 오프셋 [0, −20, +20, −10, +10] 순으로 "가로선 + 각 핀 세로선"을 try_fixed. 핀이 모두 같은 x면 세로선 하나. (위 핀들보다 아래, 아래 핀들보다 위에서만.)
5. **가로 수동소자 리드**: 핀에서 바깥으로 곧게 가다가 그 넷의 세로선(다른 넷 없음)을 만나면 확정.
6. **cross-coupled X**: inward cross-coupled 쌍마다 각 소자 드레인 세로선 위 10px 지점에서 상대 게이트 핀까지 **대각선**. 시작점 칸에 접점 점 + 노드 표시, 대각선이 지나는 칸은 hard, 상대 게이트 핀은 이미 연결된 것으로 처리.
7. **포트 핀 계획(배선 전에)**:
   - 핀이 하나뿐인 포트(게이트 입력 등) → 그 핀 끝에 Virtuoso 핀(방향 = 핀 반대쪽, 종류 = 역할).
   - 게이트만 여러 개이고 서로 멀면(bbox 가로+세로 > 240, NAND/NOR 입력) → 첫 게이트에 핀, 나머지는 같은 이름표.
   - 그 외 포트 넷 → 그리기 영역 가장자리(심볼·라벨·이미 놓은 핀 글자 범위 ±30)에 핀을 두고 배선에 포함. 쪽: 전역 대칭이면 넷 x 평균이 축 왼쪽→왼쪽, 오른쪽→오른쪽, **축 위이고 입력이면 축 아래에서 위로**(CTLE VBIAS), 대칭이 아니면 입력 왼쪽·나머지 오른쪽. 붙는 높이: 그 넷 트리에서 "세로 직선이고 차수 2인 칸" 중 가장 바깥 → 넷 랭크 y에 가까운 순 → 위쪽 먼저, 같은 쪽 다른 핀과 20px 이상 떨어진 첫 후보.
   - VSS가 포트면 왼쪽 아래(접지 기호들 중 가장 낮은 y)에 입출력 핀 + 20px 선 + 접지 기호.
   - 핀 몸통 영역은 hard, 이름 글자 영역은 soft 40.
8. **신호 넷**: (랭크 있는 넷 먼저, bbox 작은 것 먼저) 순서로 배선. 핀 하나뿐인 비포트 넷은 이름표.
9. **넷 이름표**(`lbl-net`, 기본 숨김): 포트가 아닌 배선된 넷. 가로 선분의 1/2, 1/4, 3/4 위치(글자 위 5px) 또는 세로 선분 옆 후보 중 겹침 점수 최소.
10. 최종 범위 = 모든 심볼·라벨·선·레일·핀 글자의 범위 + 여백 36.

---

## 8. 블록 레벨 배치 (layout_block)

상수: LAYER_GAP=170, STACK_GAP=90, PORT_DX=130.
1. 인스턴스 핀 역할 = 하위 셀 포트 역할. 전원/접지 핀은 심볼에서 **숨김**(검증 시 그 넷이 전원인지 확인).
2. 데이터 그래프: out 핀 → 같은 넷의 in/inout 핀. 입력 포트가 들어가는 블록부터 DFS, **되돌아오는 간선 = feedback**(그 입력 핀은 아래쪽).
3. 층 = feedback 뺀 최장경로. 핀 위치: in→왼쪽, out→오른쪽, clk→아래(DFF는 ▷ 표시), feedback→아래, bias→위. 화살촉은 왼쪽·아래 핀. 극성(+/−)은 이름 짝으로 (summer는 표시 안 함).
4. x: 층마다 그 층 최대 폭 + LAYER_GAP 누적, 층 안 블록은 가운데 정렬. y: 층 안 정렬은 연결된 driver 핀 y 평균, **첫 왼쪽 핀이 driver 출력 핀과 같은 높이**가 되게, 겹치면 아래로(STACK_GAP).
5. **혼자 있는 R/C/L**: 신호 쪽 핀 위, 전원 쪽 아래로 세우고 그 넷의 driver 핀 옆(±60, 같은 넷 k번째는 +50k), y = driver y + 90, 블록과 겹치면 오른쪽으로 40씩. 전원 쪽 핀은 10px 선 + 접지/VDD 기호.
6. 포트: out → 오른쪽 (bx1+130, driver 핀 y), 아래로 들어가는 핀에 연결되면 → 첫 그런 핀 바로 아래 (x, by1+70)에서 위로, 나머지 → 왼쪽 (bx0−130, 첫 sink 핀 y). 같은 쪽 y가 ±10 안에 겹치면 20씩 밀기. bias 이름 넷(포트이고 역할 bias, 또는 out 없이 bias 핀만)은 배선하지 않고 각 핀에서 20px 선: **포트면 첫 번째에 Virtuoso 핀**, 나머지는 회전된 이름(세로 글씨). 전원/접지 포트는 왼쪽 위(VDD)·왼쪽 아래(VSS)에 입출력 핀 + 20px 선 + VDD/접지 기호.
7. 배선 순서: 데이터 넷 → 위/아래 핀이 있는 넷(feedback) → 클럭, 같은 범주는 퍼짐이 작은 것 먼저.
8. **인스턴스 라벨**은 배선 후 배치: 후보 [아래 가운데(body 아래 16), 위 가운데, 오른쪽 아래, 왼쪽 아래, 오른쪽 위, 왼쪽 위, bbox 아래/위, …] 중 다른 글씨(100), 배선·심볼 선(60), 몸통(60)과 겹침 점수가 최소(0이면 즉시)인 곳.
9. 내부 넷 이름표(`lbl-net`), 최종 범위 refit.

---

## 9. 심볼 좌표 (로컬 좌표, 단위 px, y는 아래로 +)

변환 순서: mirror(x→−x) → 시계방향 90°×rot → 평행이동. 핀 방향도 같이 변환(mirror L↔R, rot U→R→D→L).

**MOSFET (게이트 왼쪽 기준)**
```
선: 게이트 리드 (-30,0)-(-20,0) / 게이트판 (-20,-13)-(-20,13) [class "sym gate"]
    채널 (-11,-15)-(-11,15) [class "sym chan"] / 위 꺾임 (-11,-15)-(0,-15), (0,-15)-(0,-30)
    아래 꺾임 (-11,15)-(0,15), (0,15)-(0,30)
NMOS: 핀 d(0,-30,U) g(-30,0,L) s(0,30,D), 화살표 다각형 (-0.6,15)(-6.4,11)(-6.4,19)
PMOS: 핀 s(0,-30,U) g(-30,0,L) d(0,30,D), 화살표 다각형 (-10.4,-15)(-4.6,-19)(-4.6,-11)
keepout: (-21,-29,1,29), (-29,-1,-20,1)
라벨(시작 정렬): 이름 (6,-12) [lbl-name], W/L (6,1) [lbl-wl], m (6,13) [lbl-wl]
```
**저항**: 리드 (0,-30)-(0,-18), 지그재그 (0,-18) → (±6, −15+6i) i=0..5 교대(+6부터) → (0,18), 리드 (0,18)-(0,30). 핀 p(0,-30,U) n(0,30,D). keepout (-7,-29,7,29). 라벨 (11,-5) 이름, (11,8) 값.
**커패시터**: (0,-30)-(0,-4), 판 (-10,-4)-(10,-4), (-10,4)-(10,4) [sym plate], (0,4)-(0,30). keepout (-11,-29,11,29). 라벨 (14,-5),(14,8).
**인덕터**: 리드 ±(16~30), 반원 4개 중심 y = −12+8i, 반지름 4 (polyline 9점). keepout (-6,-29,6,29).
**전압/전류원**: 원 r=12, 리드 ±(12~30). V는 + (0,-3), − (0,8) 글자, I는 화살표.
**generic 박스**: 폭 60, 핀 왼쪽 반/오른쪽 반, 20 간격, 리드 20.
**접지 기호** (x,y 아래로): (x,y)-(x,y+8), (x−9,y+8)-(x+9,y+8), (x−6,y+12)-(x+6,y+12), (x−3,y+16)-(x+3,y+16).
**VDD 기호**: (x,y)-(x,y−8), (x−8,y−8)-(x+8,y−8), 이름 (x, y−12).
**Virtuoso 핀** (붙는 점 (0,0), 회로는 +x 방향, 몸통은 −x로):
```
in : (0,0)(-7,-5)(-20,-5)(-20,5)(-7,5)        # 회로 쪽을 가리킴
out: (0,-5)(-13,-5)(-20,0)(-13,5)(0,5)        # 바깥을 가리킴
io : (0,0)(-5,-5)(-15,-5)(-20,0)(-15,5)(-5,5) # 육각형
```
방향 d(회로 쪽) R/L/U/D로 회전: 로컬 +x → d 벡터, 로컬 +y → (−d.y, d.x). 이름 글자: d=R → (x−25, y+3.5) 끝 정렬, d=L → (x+25, y+3.5) 시작 정렬, d=D(몸통 위) → (x+3.5, y−25) −90° 회전 시작 정렬, d=U(몸통 아래) → (x+3.5, y+25) −90° 회전 끝 정렬. 몸통 keepout: 붙는 점에서 −6~−20, 폭 ±6.

**블록 심볼** (원점 = 몸통 왼쪽 위, 핀 끝은 10 격자 위)
- `_spread(n, center, pitch)`: center 기준 pitch 간격 n개, 10 단위 반올림.
- **amp/inv(삼각형)**: h = ceil20(max(80, 20(nL+1)+20)), w = max(80, floor20(0.9h)), 꼭짓점 (0,0)(w,h/2)(0,h). 왼쪽 핀 x=−20, y=spread(nL, h/2, 20), 리드 −20→0, +/− 글자 (7, y+3.5). 오른쪽 핀: 경사 위 x_e = w(1−|y−h/2|/(h/2)), 핀 x = ceil10(max(x_e, tip)+20). inv는 (w+5,h/2) 반지름 5 동그라미, tip=w+10. 위/아래 핀 x=20(i+1), 경사면에서 y=−20 / h+20. 제목 (0.36w, h/2+4).
- **sum(Σ원)**: r = ceil10(max(30, 10·max(nB,nT,1)+10)), 중심 (r+10, r+10). 좌우 핀 x=−10 / 2cx+10, y=spread(…, cy, 20), 원 경계까지 리드. 위/아래 핀 x=spread(…, cx, 20), y=−10 / 2cy+10. Σ 글자 22px.
- **게이트(nand/and/nor/or/xor)**: h = ceil20(max(60, 20(n+1))), w=h. AND 모양: (0,0)→(w/2,0)→반원→(0,h). OR 모양: 뒤쪽 곡선 10·sin(πy/h). nand/nor는 (w+5,h/2) 동그라미.
- **박스(box/dff/latch/mux)**: 제목 폭 tw = len×13×0.62+16, 핀 글자 폭 = 최대 글자수×9×0.58, 위/아래 핀 간격 tb_pitch = max(40, ceil10(위·아래 글자폭+14)), w = ceil20(max(100, tw + 왼쪽 글자폭 + 오른쪽 글자폭 + 30, tb_pitch×(nTB+1))), h = ceil20(max(80, 20(max(nL,nR,1)+1)+20)). 핀 리드 20, 핀 이름 안쪽(왼 x=5 시작, 오른 x=w−5 끝, 위 y=12, 아래 y=h−6; DFF 클럭은 ▷ (x−6,h)(x,h−9)(x+6,h) + 이름 y=h−12). mux는 사다리꼴. 제목 (w/2, h/2+5).
- 블록 keepout = 몸통 ±9 (선이 외곽선에 붙지 않게).
- 입력 화살촉: 끝점에서 길이 8, 폭 ±4 채운 삼각형 [class arrowhead].

---

## 10. HTML / SVG 구조 (뷰어와 검증기가 의존하는 약속)

페이지: `<header class="bar">` (`#crumbs` 경로 + `.tools`: 체크박스 `data-toggle="wl|val|name|net"`(라벨 "W/L·m", "R/C 값", "소자 이름", "넷 이름"; net만 기본 꺼짐), `#btn-up` "↑ 상위", `#btn-fit` "⤢ 맞춤", `#btn-ppt` "⬇ PPT", `#cell-jump` 선택 목록) / `<main>` (`#canvas` 안에 셀마다 `<div class="view" data-cell hidden><svg class="sch">`, `#tip` 툴팁) + `<aside id="side">`. 데이터: `<script id="hsch-data" type="application/json">`(`</`는 `<\/`로), `<script id="hsch-pptx" type="application/octet-stream" data-name="파일.pptx">base64</script>`.

SVG (뷰마다): `<svg class="sch" data-cell viewBox data-bounds="x0,y0,x1,y1">` 안에 레이어 순서:
1. `g.layer-wires`: `<line class="wire[ diag]" data-net x1 y1 x2 y2>`
2. `g.layer-syms`: 소자 `<g class="symg dev" data-inst data-type data-keep="x0,y0,x1,y1;…">`, 블록 `<g class="symg blkg clickable" data-inst data-ref data-hidden="숨긴핀,…" data-keep data-body="x0,y0,x1,y1">` + 클릭 영역 `<rect class="hit">`. 안에 심볼 선/다각형/원/글자, 라벨 `<text class="devlbl"><tspan class="lbl-name|lbl-wl|lbl-val|lbl-cell">`.
   ※ 블록 그룹 class에 `blk`를 쓰면 안 된다(§15).
3. `g.layer-rails`: `<g class="rail" data-net data-ax data-ay>` 접지/VDD 기호.
4. `g.layer-dots`: `<circle class="dot" r=2.6>`.
5. `g.layer-labels`: 핀/이름표 `<g class="term[ port]" data-net data-ax data-ay>` + (Virtuoso 핀이면) `<polygon class="vpin vpin-in|out|io">` + `<text class="term-t" [transform="rotate(-90 x y)" data-rot="1"]>이름</text>`, 넷 이름 `<text class="netlabel lbl-net|lbl-port|lbl-rail" data-net data-ax data-ay>`.
6. `g.layer-pins`: `<circle class="pin" data-inst data-pin data-net r=2>` (투명, 검증용). 포트 핀은 `data-inst="PORT"`.

viewer info JSON: `{"top", "cells": {셀: {"display","label","class","reason","auto","ports","roles","insts": {이름: {"type","ref","auto","pins": {핀: 넷}, "params": {w,l,m,r,c}}}, "warnings","verify": {"ok","errors","lint": {"crossings","text_overlaps","warnings"}}}}}` (MOS bulk 핀 제외).

**CSS (그대로)**: 색 변수 --ink #111, --paper #fff, --ui-bg #f6f6f4, --ui-fg #222, --ui-mute #6b6b6b, --ui-line #d9d9d4, --accent #d0451b, --wl #1d5fa8, --net #6b4f9e, --blk-hover #fff4e5. 선 굵기: .sym/.blk/.wire 1.6, .sym.chan 3.4, .sym.gate 2, .sym.plate 2.2, 강조 .hl.wire 2.4(accent). 글자: 그림 글꼴 "Helvetica Neue", Helvetica, Arial; devlbl 9px, netlabel 10px, term-t 10px 600, pin-t 9px #333, blk-t 13px 700, sum-t 22px, pol-t 12px 700. .lbl-name #333 italic, .lbl-wl/.lbl-val #1d5fa8, .lbl-net #6b4f9e italic. Virtuoso 핀 `.vpin { fill:#e8261c; stroke:#8c0d07; stroke-width:.9 }`. 토글: `body.hide-wl .lbl-wl{display:none}` 등, `body:not(.show-net) .lbl-net{display:none}`. **`.canvas { touch-action:none; overscroll-behavior:contain }`, `.bar, .side { touch-action: manipulation }`**. 760px 이하에서는 사이드 패널이 아래(최대 34vh). 종이는 흰색 유지.

---

## 11. 뷰어 동작 (viewer.js, 외부 라이브러리 없음)

- **이동**: 시작 시 top 셀을 맞춤(fit) 상태로. 블록 클릭/탭 → `stack.push({cell: ref, inst})`, 경로 갱신. 경로의 이전 항목 클릭 → 그 단계로. `↑ 상위`/Esc/Backspace → 한 단계 위(맨 위에서는 아무 일 없음). 선택 목록 → 그 셀로(경로 초기화). 뷰마다 viewBox 기억.
- **뷰 전환 시 반드시**: 강조 해제, **툴팁 숨김**, 진행 중 제스처 초기화.
- **토글**: 체크박스 → body class (hide-wl/hide-val/hide-name/show-net), localStorage `hsch:t-<key>`에 저장(모든 접근 try/catch).
- **신뢰할 수 있는 탭 `onTap(el, fn)`**: 터치(마우스 아님)는 pointerdown 위치 기억 → pointerup에서 이동 ≤ 12px이면 즉시 fn 실행, 이후 800ms 안의 click은 preventDefault+stopPropagation(캡처 단계)으로 버림. 마우스/키보드는 일반 click. 체크박스는 터치면 직접 checked 반전 + 적용, click이면 기본 동작(change 이벤트)으로 적용. 경로 링크·상위·맞춤·PPT 버튼 모두 onTap.
- **제스처**: 포인터를 id별로 추적. 한 개 = 이동(마우스 4px, 터치 12px 넘으면 드래그 시작, 이때만 `setPointerCapture`), 두 개 = 핀치 확대/축소(시작 시 두 손가락 가운데·거리 기억, 기준점 고정 확대 + 가운데 이동만큼 평행이동). pointerup/pointercancel/lostpointercapture로 종료하되 **lostpointercapture는 target이 canvas일 때만**. 손가락이 하나 남으면 그 위치로 제스처 재시작(튀지 않게). 휠: `k = exp(deltaY×0.0015)`로 커서 기준 확대. 확대 범위는 원래 폭의 **0.05배~20배**로 제한.
- **캔버스 탭/클릭**: 드래그가 아니었으면 — 블록이면 하위로, 넷 요소면 강조 고정 토글(터치면 툴팁도), 소자면(터치) 툴팁 표시, 빈 곳이면 강조·툴팁 해제. 터치 탭은 pointerup에서 처리하고 뒤따르는 click(800ms)은 무시. 더블클릭 → 맞춤.
- **툴팁**: 마우스 이동 시 소자 = `이름 (type)` + W/L/m/R/C + (블록이면 `→ 하위셀 (클릭해서 열기)`) + `핀 : 넷` 목록, 넷 = `net: 이름`. **터치 후 800ms 동안의 호환 마우스 이벤트는 무시**(새 화면에 툴팁이 뜨는 것 방지).
- **강조**: 같은 data-net 요소 전부 `.hl`. 사이드 패널 넷 링크에 마우스 올리면 강조.
- **사이드 패널**: 표시 이름, 라벨(+ "· 자동 생성 블록"), `인식 근거: …`, (하위일 때) `포트 연결 (inst @ 부모)` 표, `포트` 표(역할 / 이름), `검증`: `✅ 연결 일치 (원본 netlist와 동일)` 또는 ❌ + 오류, `교차 N · 경고 N`, 경고 최대 8개, `사용법` 문구.
- **PPT 버튼**: `#hsch-pptx`의 base64 → Uint8Array → Blob(pptx MIME) → `a.download` 클릭 → 2초 뒤 URL 해제.
- **스크립트 훅**: `window.HSCH = {show(cell), path([inst…]), cells()}`.

---

## 12. PPTX 내보내기 (python-pptx)

- 슬라이드 13.333×7.5 in, 빈 레이아웃, **셀마다 1장**(뷰 순서). 그림 영역: 좌우 여백 0.35in, 위 0.75in, 아래 0.3in에 맞춰 축척(EMU/px) 후 가운데.
- 제목줄: 표시 이름(20pt 굵게) + 라벨 + 검증 OK면 `  ·  connectivity verified`(11pt 회색). 하위 셀이면 오른쪽 위 `▲ 부모셀`(파랑) → 부모 슬라이드로 click_action.
- 넷마다 그룹 `net <이름>`: 선분 = 직선 connector, 접점 = 채운 원. 소자/블록마다 그룹(이름 = 인스턴스): 블록은 몸통 크기의 **완전 투명 사각형**(alpha 0) + click_action → 그 셀 슬라이드. 심볼 선 = connector, polyline = freeform(닫힌 블록 외곽은 흰색 채움), 다각형 = 검정 채움 freeform, 원 = 타원, 글자 = 텍스트 상자(여백 0, 줄바꿈 없음, 정렬 = anchor). 레일 그룹, 핀 그룹 `pin <이름>`(빨간 freeform #e8261c 테두리 #8c0d07 + 이름), 넷 이름표(`lbl-net`은 기본 제외 — 뷰어 기본값과 같게).
- 선 굵기 pt = px × (EMU/px) / 12700, 굵기 표 chan 3.2 / gate 2.0 / plate 2.2 / 기본 1.6. 글자 크기도 같은 환산, 글꼴 Arial, 색은 §10과 같게. 회전 글자는 −90°(rotation 270)이고 회전 중심을 맞춰 배치.
- 메모: `셀: 라벨. Recognised because: 근거. Ports: …`.
- 제약(사용자에게 알릴 것): PowerPoint에서 소자를 옮겨도 선은 따라오지 않음.

---

## 13. 검증기 (verify.py) — 그림에서 연결을 다시 읽어 비교

HTML을 파싱해 뷰마다 wire 선분, pin(inst, pin, x, y), dot, 이름(rail의 data-net, term의 글자, netlabel의 글자 + 각각의 앵커 좌표), 심볼(keep, body, hidden), 모든 text(종류·글자·상자), 심볼 내부 선분을 모은다. **wire의 data-net은 연결 추출에 쓰지 않는다.**

연결 추출(사람이 스키매틱을 읽는 방식):
- 관심점 = 선분 끝점 ∪ 핀 위치 ∪ 이름 앵커. 각 점에서 그 점이 끝점인 선분(E), 내부에 있는 선분(I)을 구한다(대각선 포함, 점-선분 거리 < 0.5).
- E가 있으면 E와 I 전부 연결(T 접점). E 없이 I만 2개 이상이면 **교차 = 연결 안 됨**.
- 핀은 그 점에 닿은 모든 선분과 연결, 같은 위치 핀끼리도 연결. 이름 앵커는 닿은 선분/핀과 연결(아무것도 안 닿으면 오류), **같은 이름끼리 연결**.

비교: netlist의 (소자, 핀)(MOS bulk 제외, 블록의 숨긴 핀은 넷이 전원/접지인지 확인) ↔ 그림의 그룹. 오류: 안 그려진 핀 / netlist에 없는 핀 / **OPEN**(한 넷이 여러 조각) / **SHORT**(여러 넷이 한 그룹) / 이름표가 다른 넷 위 / 포트가 그림 어디에도 없음. PORT 핀은 자기 이름 넷.

lint (모두 0이어야 함): 교차 수(정보), 4방향 접점, 점 없는 T 접점, 접점 아닌 점, 배선이 심볼 keepout 관통, 핀이 선분 한가운데, **글씨-글씨 겹침, 글씨-배선 겹침, 글씨-심볼 선 겹침, 글씨-블록 몸통 겹침**(자기 블록 안 글씨는 제외), σ 쌍이 같은 높이 아님 / 거울상 아님(게이트 x 오프셋이 반대가 아님), PMOS가 NMOS보다 아래.
글자 상자 추정: 폭 = 글자수×크기×0.58, 높이 −0.75×크기 ~ +0.2×크기, 정렬 반영, −90° 회전 반영. 크기: devlbl 9, netlabel 10, term-t 10, pin-t 9, blk-t 13, sum-t 22, pol-t 12, rail-t 10, sym-t 10.

---

## 14. 검증 절차 (완성 조건)

1. **단위·통합 테스트** `python3 -m unittest discover -s tests -v` — 15개 전부 OK:
   파서(SI 값, `+`/`$`/대소문자, 모델명 N/P), 자동 블록(DFE_1TAP 안 8소자, 포트), flatten 동일, 포트 역할(QP=out, CLK=clk, VBIAS=bias, 자동 블록 OUTP=in), 인식(ctle/latch/dff/summer/nand/inverter), 두 netlist 전 뷰 연결 PASS + lint 0, **전역 대칭**(CTLE·latch의 모든 쌍이 같은 축, MB가 축 위), 토글 4개·외부 스크립트 없음, 검증기가 선 삭제(OPEN)·잘못된 연결(SHORT)·글씨 겹침을 잡는지, **모든 포트에 Virtuoso 핀**, PPTX(슬라이드 수 = 뷰 수, 포트 이름이 편집 가능한 글자로 있음, 선 수 = 배선 수, 블록 점프가 맞는 슬라이드, 모든 도형이 슬라이드 안).
2. **뷰어 자동 점검** `node scripts/ui_selftest.js OUT.html` → 두 예제 각각 `100 passed, 0 failed`, `105 passed, 0 failed` 수준. 데스크톱: 토글 4개(그림 위치 그대로, 라벨만 변화, 두 번 누르면 복원), 마우스 드래그 1:1, 드래그 후 토글, 휠 확대·축소 제한, 맞춤, 더블클릭, 호버 툴팁/해제, 모든 블록 클릭→하위→상위, 가장 깊은 셀까지, Esc/Backspace/F, 토글 클릭 뒤 Esc, 경로 클릭, 맨 위에서 상위, 선택 목록 전부, 넷 클릭 강조/해제, 사이드 패널 강조, **PPT 다운로드(.pptx, PK 시작, 10KB 이상)**, 새로고침 후 토글 유지, 창 크기 변경. 폰(Pixel 7, 실제 터치 이벤트): 한 손가락 이동 1:1 + pointercancel 없음, **이동 직후 엄지 탭(3~5px 흔들림)으로 토글해도 그림 그대로**, 핀치 확대/축소, 핀치 후 토글, 맞춤, 핀치 직후 블록 탭, 블록 탭 후 툴팁 없음, 블록 안 토글, 소자 탭 툴팁/빈 곳 탭 해제, 상위, **이동 직후 블록 탭**, 경로 탭, 가로 화면, JS 오류 없음.
3. **눈 확인**: `screenshot.js`로 모든 뷰 PNG, PPTX는 `soffice --headless --convert-to pdf OUT.pptx` + `pdftoppm -r 70 -png OUT.pdf slide`로 확인.

### 기준 결과 (부록 A netlist)
| 뷰 | 결과 | 교차 | 모양 |
|---|---|---|---|
| INPUT_BUFFER_SYSTEM | PASS, lint 0 | 0 | CTLE 삼각형 → DFE 박스, 클럭 아래, bias 위 |
| CTLE | PASS | 0 | 전역 대칭, R_S 위 C_S 아래, VBIAS 축 아래에서 |
| DFE_1TAP | PASS | 5 | Σ(auto) → DFF, feedback 아래로 |
| DFE_1TAP__AUTO0 (Summer) | PASS | 2 | main 쌍 + tap 쌍 각자 대칭, 출력 버스 두 높이, SUMP/SUMN 오른쪽 |
| CML_DFF | PASS | 1 | LATCH → LATCH, 클럭 교차 |
| CML_LATCH | PASS | 2 | M1 M3 \| M4 M2 전역 대칭, 가운데 X, M5/M6 거울, MB 축 |
인식: INPUT_BUFFER_SYSTEM→buffer(이름), CTLE→ctle, DFE_1TAP→dfe, DFE_1TAP__AUTO0→summer, CML_DFF→dff, CML_LATCH→latch.

---

## 15. 겪었던 버그와 해결 (같은 실수 반복 금지)

1. **블록 글자가 두껍게 번짐**: 블록 그룹에 class `blk`를 붙이면 `.blk{stroke}`가 글자에 상속됨 → 그룹 class는 `blkg`.
2. **선이 블록 외곽선을 타고 지나감**: keepout을 몸통 크기로 하면 경계 칸이 비어 있음 → 몸통 ±9로 키움.
3. **latch tail 선이 계단식**: 미로 배선만 쓰면 생김 → 노드 버스 선배선(§7.2-4).
4. **글씨 겹침 검사가 놓침**: 일부 글자만 비교하고 핀 리드(심볼 선)를 빼먹음 → 모든 text와 심볼 선분까지 비교, 일부러 겹침을 넣어 잡히는지 테스트.
5. **블록을 탭하면 하위 화면에 툴팁이 남음**: 화면 전환 때 툴팁을 안 숨김 + 탭 뒤 호환 mousemove → 전환 시 숨기고 터치 후 800ms 마우스 이벤트 무시.
6. **폰에서 이동 후 토글을 누르면 그림이 날아감**: 캔버스에 touch-action이 없어 브라우저가 이동을 가로채 pointercancel, 그걸 처리 안 해 드래그 상태가 남음 → touch-action:none, 포인터 id 추적, cancel 처리.
7. **pointerdown에서 바로 setPointerCapture → 블록/넷 클릭이 안 됨**(click 대상이 canvas로 바뀜) → 드래그가 실제로 시작될 때만 capture.
8. **capture를 넘겨받으면 원래 요소의 lostpointercapture가 버블링되어 드래그가 끊김** → target이 canvas일 때만 종료.
9. **엄지 탭의 3~7px 흔들림을 드래그로 오인** → 터치 허용 12px.
10. **이동 직후 0.3초 안의 탭이 무시됨**(브라우저의 fling 탭 억제) → pointerup에서 직접 실행하는 onTap.
11. **같은 체크박스 빠른 두 번 탭이 더블탭 확대로 먹힘** → 툴바 touch-action: manipulation.
12. **축소 무제한 → viewBox 숫자가 넘쳐 SVG 오류** → 0.05~20배 제한.
13. **포트 핀 붙는 위치가 집합 순회 순서에 따라 위/아래로 달라져 대칭이 깨짐** → 정렬 키에 y를 넣어 항상 위쪽 먼저.
14. **공유 bias(CTLE VBIAS) 핀을 왼쪽에 두면 소자를 돌아가는 우회 배선** → 대칭 셀에서는 축 아래에서 위로.
15. **블록 폭이 핀 이름 길이를 고려 안 해 VBIAS_MAIN 등이 겹침** → 글자 폭으로 박스 폭 계산, 위/아래 이름은 세로 회전.
16. 셸 heredoc 안에 `$$` 같은 문자열이 있으면 일부 안전 검사가 명령을 거부함 → 파일 편집 도구를 쓸 것.
17. 출력 폴더가 없으면 HTML 저장에서 멈춤 → build.py가 출력 폴더를 먼저 만든다.

---

## 부록 A. 테스트 netlist (tests/netlists/input_buffer_system.sp)
```spice
.SUBCKT CTLE INP INN OUTP OUTN VBIAS VDD VSS
RLP VDD OUTP 600
RLN VDD OUTN 600
M1 OUTP INP SP VSS NCH W=16u L=45n
M2 OUTN INN SN VSS NCH W=16u L=45n
RS SP SN 1000
CS SP SN 150f
MBP SP VBIAS VSS VSS NCH W=32u L=90n
MBN SN VBIAS VSS VSS NCH W=32u L=90n
.ENDS CTLE

.SUBCKT CML_LATCH DP DN CLK CLKB QP QN VBIAS VDD VSS
RLP VDD QP 500
RLN VDD QN 500
M1 QP DP TAIL_T VSS NCH W=12u L=45n
M2 QN DN TAIL_T VSS NCH W=12u L=45n
M3 QP QN TAIL_H VSS NCH W=12u L=45n
M4 QN QP TAIL_H VSS NCH W=12u L=45n
M5 TAIL_T CLK TAIL VSS NCH W=16u L=45n
M6 TAIL_H CLKB TAIL VSS NCH W=16u L=45n
MB TAIL VBIAS VSS VSS NCH W=32u L=90n
.ENDS CML_LATCH

.SUBCKT CML_DFF DP DN CLK CLKB QP QN VBIAS VDD VSS
X_MASTER DP DN CLKB CLK MP MN VBIAS VDD VSS CML_LATCH
X_SLAVE MP MN CLK CLKB QP QN VBIAS VDD VSS CML_LATCH
.ENDS CML_DFF

.SUBCKT DFE_1TAP INP INN CLK CLKB OUTP OUTN VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS
RLP VDD SUMP 500
RLN VDD SUMN 500
M1 SUMP INP TAIL_M VSS NCH W=20u L=45n
M2 SUMN INN TAIL_M VSS NCH W=20u L=45n
MB_M TAIL_M VBIAS_MAIN VSS VSS NCH W=40u L=90n
M3 SUMP OUTP TAIL_T1 VSS NCH W=8u L=45n
M4 SUMN OUTN TAIL_T1 VSS NCH W=8u L=45n
MB_T1 TAIL_T1 VBIAS_TAP VSS VSS NCH W=16u L=90n
X_DFF SUMP SUMN CLK CLKB OUTP OUTN VBIAS_DFF VDD VSS CML_DFF
.ENDS DFE_1TAP

.SUBCKT INPUT_BUFFER_SYSTEM RX_INP RX_INN CLK CLKB DOUTP DOUTN VBIAS_CTLE VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS
X_CTLE RX_INP RX_INN CTLE_OUTP CTLE_OUTN VBIAS_CTLE VDD VSS CTLE
X_DFE CTLE_OUTP CTLE_OUTN CLK CLKB DOUTP DOUTN VBIAS_MAIN VBIAS_TAP VBIAS_DFF VDD VSS DFE_1TAP
.ENDS INPUT_BUFFER_SYSTEM
```

## 부록 B. Virtuoso 형식 테스트 (tests/netlists/virtuoso_style.sp)
소문자 이름, `+` 줄 이어쓰기, `$` 주석, `nch_lvt/pch_lvt` 모델, PMOS 부하 5T OTA, 인버터, NAND2, 블록과 R/C가 섞인 top. 기대: 모든 뷰 PASS, ota5t는 대칭(PMOS 미러 안쪽), nand2→nand(병렬 PMOS 위·직렬 NMOS 아래, A/B는 각 게이트에 이름), top_mixed는 c0/r0가 접지 기호와 함께 소자 그대로.
```spice
** Generated for: hspiceD
** Library name: test_lib
** Cell name: top_mixed
** View name: schematic
.subckt ota5t vinp vinn vout vbn vdd vss
mm1 net1 vinp tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm2 vout vinn tail vss nch_lvt w=4e-6 l=100e-9 m=1 nf=2
mm3 net1 net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm4 vout net1 vdd vdd pch_lvt w=2e-6 l=100e-9 m=1
mm5 tail vbn vss vss nch_lvt w=8e-6
+ l=200e-9 m=2
.ends ota5t
** Cell name: inv
.subckt inv in out vdd vss
mn0 out in vss vss nch_lvt w=1e-6 l=45e-9 $ pull-down
mp0 out in vdd vdd pch_lvt w=2e-6 l=45e-9
.ends inv
.SUBCKT nand2 A B Y VDD VSS
MN1 Y A X VSS nch_lvt W=1u L=45n
MN2 X B VSS VSS nch_lvt W=1u L=45n
MP1 Y A VDD VDD pch_lvt W=1u L=45n
MP2 Y B VDD VDD pch_lvt W=1u L=45n
.ENDS
.subckt top_mixed a b o en vb vdd vss
xi0 a b n1 vb vdd vss ota5t
xi1 n1 n2 vdd vss inv
xi3 n2 en n3 vdd vss nand2
xi2 n3 o vdd vss inv
c0 n1 vss 10f
r0 o vss 1k
.ends top_mixed
```
