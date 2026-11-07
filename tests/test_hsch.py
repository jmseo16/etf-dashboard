"""Regression tests:  python3 -m unittest discover -s tests -v"""
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hspice-schematic", "scripts"))

from build import build  # noqa: E402
from hsch.analyze import classify_all, extract_auto_blocks, flatten, port_roles  # noqa: E402
from hsch.parser import parse_file, parse_text, parse_value  # noqa: E402
from hsch.verify import check_view, parse_html, text_box  # noqa: E402

NET = os.path.join(ROOT, "tests", "netlists")
IBS = os.path.join(NET, "input_buffer_system.sp")
VIRT = os.path.join(NET, "virtuoso_style.sp")


class TestParser(unittest.TestCase):
    def test_values(self):
        self.assertAlmostEqual(parse_value("16u"), 16e-6)
        self.assertAlmostEqual(parse_value("45n"), 45e-9)
        self.assertAlmostEqual(parse_value("150f"), 150e-15)
        self.assertAlmostEqual(parse_value("1k"), 1e3)
        self.assertAlmostEqual(parse_value("2meg"), 2e6)
        self.assertAlmostEqual(parse_value("1.6e-05"), 1.6e-5)
        self.assertAlmostEqual(parse_value("10fF"), 10e-15)
        self.assertIsNone(parse_value("'w1*2'"))

    def test_continuation_comments_case(self):
        ir = parse_text("""
* comment
.SUBCKT a in out vdd vss
mm1 out in vss vss nch w=1u $ inline comment
+ l = 45n
.ends
.subckt TOP x y vdd vss
xi0 x y vdd vss A
.ends
""")
        d = ir["cells"]["a"]["devices"][0]
        self.assertEqual(d["params"]["l"], "45n")
        self.assertEqual(d["type"], "nmos")
        self.assertEqual(ir["top"], "TOP")
        x = ir["cells"]["TOP"]["devices"][0]
        self.assertEqual(x["ref"], "a")             # case-insensitive subckt lookup
        self.assertEqual(dict(x["pins"])["in"], "x")

    def test_mos_type_from_model(self):
        ir = parse_file(VIRT)
        types = {d["name"]: d["type"] for d in ir["cells"]["ota5t"]["devices"]}
        self.assertEqual(types["mm3"], "pmos")
        self.assertEqual(types["mm1"], "nmos")
        mm5 = [d for d in ir["cells"]["ota5t"]["devices"] if d["name"] == "mm5"][0]
        self.assertEqual(mm5["params"]["l"], "200e-9")  # '+' continuation


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.ir0 = parse_file(IBS)
        self.ir = extract_auto_blocks(self.ir0)

    def test_auto_block(self):
        dfe = self.ir["cells"]["DFE_1TAP"]
        kinds = sorted(d["kind"] for d in dfe["devices"])
        self.assertEqual(kinds, ["X", "X"])
        auto = self.ir["cells"]["DFE_1TAP__AUTO0"]
        self.assertEqual(len(auto["devices"]), 8)
        for p in ("INP", "INN", "OUTP", "OUTN", "SUMP", "SUMN", "VBIAS_MAIN", "VBIAS_TAP"):
            self.assertIn(p, auto["ports"])
        self.assertNotIn("TAIL_M", auto["ports"])

    def test_flatten_unchanged(self):
        self.assertEqual(flatten(self.ir0, self.ir0["top"]), flatten(self.ir, self.ir["top"]))

    def test_roles(self):
        r = port_roles(self.ir)
        self.assertEqual(r["CML_LATCH"]["QP"], "out")
        self.assertEqual(r["CML_LATCH"]["CLK"], "clk")
        self.assertEqual(r["CTLE"]["VBIAS"], "bias")
        self.assertEqual(r["DFE_1TAP"]["OUTP"], "out")
        self.assertEqual(r["DFE_1TAP__AUTO0"]["OUTP"], "in")   # tap input inside the summer

    def test_classes(self):
        c = classify_all(self.ir)
        self.assertEqual(c["CTLE"]["class"], "ctle")
        self.assertEqual(c["CML_LATCH"]["class"], "latch")
        self.assertEqual(c["CML_DFF"]["class"], "dff")
        self.assertEqual(c["DFE_1TAP__AUTO0"]["class"], "summer")
        ir2 = extract_auto_blocks(parse_file(VIRT))
        c2 = classify_all(ir2)
        self.assertEqual(c2["nand2"]["class"], "nand")
        self.assertEqual(c2["inv"]["class"], "inverter")


class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.out = {}
        for name, path in (("ibs", IBS), ("virt", VIRT)):
            html = os.path.join(cls.tmp, name + ".html")
            ok, report, scenes = build(path, html, quiet=True)
            cls.out[name] = (ok, report, scenes, html)

    def test_connectivity_and_lint_clean(self):
        for name, (ok, report, _, _) in self.out.items():
            self.assertTrue(ok, f"{name}: connectivity mismatch {report}")
            for cell, r in report.items():
                self.assertEqual(r["lint"]["warnings"], [], f"{name}/{cell}")

    def test_global_mirror_symmetry(self):
        _, _, scenes, _ = self.out["ibs"]
        pairs = {"CTLE": [("M1", "M2"), ("RLP", "RLN"), ("MBP", "MBN")],
                 "CML_LATCH": [("M1", "M2"), ("M3", "M4"), ("RLP", "RLN"), ("M5", "M6")]}
        for cell, plist in pairs.items():
            pins = {}
            for p in scenes[cell]["pins"]:
                pins.setdefault(p["inst"], []).append((p["x"], p["y"]))
            axes = set()
            for a, b in plist:
                xa = sorted(x for x, _ in pins[a])
                xb = sorted(x for x, _ in pins[b])
                axes.add((xa[0] + xb[-1]) / 2.0)
                self.assertEqual(sorted(y for _, y in pins[a]), sorted(y for _, y in pins[b]))
            self.assertEqual(len(axes), 1, f"{cell}: pairs mirrored about different axes {axes}")
        # tail device of the latch sits on the axis
        mb = [p["x"] for p in scenes["CML_LATCH"]["pins"] if p["inst"] == "MB" and p["pin"] == "d"][0]
        self.assertEqual(mb, axes.pop())

    def test_pptx_editable_and_navigable(self):
        from pptx import Presentation
        from pptx.shapes.group import GroupShape
        from pptx.util import Inches
        _, _, scenes, html = self.out["ibs"]
        prs = Presentation(os.path.splitext(html)[0] + ".pptx")
        slides = list(prs.slides)
        self.assertEqual(len(slides), len(scenes))

        def walk(shapes):
            for sh in shapes:
                yield sh
                if isinstance(sh, GroupShape):
                    yield from walk(sh.shapes)

        title_of = {sl.slide_id: cell for sl, cell in zip(slides, scenes)}   # slide order == view order
        for sl, cell in zip(slides, scenes):
            sc = scenes[cell]
            shapes = list(walk(sl.shapes))
            texts = {sh.text_frame.text for sh in shapes if sh.has_text_frame}
            for p in sc["ports"]:
                self.assertIn(p, texts, f"{cell}: port {p} missing as editable text")
            nets = [sh for sh in sl.shapes if isinstance(sh, GroupShape) and sh.name.startswith("net ")]
            n_lines = sum(1 for g in nets for sh in g.shapes if sh.shape_type == 9 or "Connector" in sh.name)
            self.assertEqual(n_lines, len(sc["wires"]), f"{cell}: wire count")
            for sh in shapes:
                if sh.name.startswith("open "):
                    ref = sh.name[5:]
                    tgt = sh.click_action.target_slide
                    self.assertIsNotNone(tgt, f"{cell}: {sh.name} has no jump")
                    self.assertEqual(title_of[tgt.slide_id], ref)
            for sh in sl.shapes:
                self.assertGreaterEqual(sh.left, 0)
                self.assertGreaterEqual(sh.top, 0)
                self.assertLessEqual(sh.left + sh.width, prs.slide_width + Inches(0.05), f"{cell}: {sh.name} off slide")
                self.assertLessEqual(sh.top + sh.height, prs.slide_height + Inches(0.05), f"{cell}: {sh.name} off slide")

    def test_every_port_has_a_virtuoso_pin(self):
        for name in ("ibs", "virt"):
            _, _, scenes, _ = self.out[name]
            for cell, sc in scenes.items():
                pins = {t["net"] for t in sc["terminals"] if t.get("vpin")}
                for p in sc["ports"]:
                    self.assertIn(p, pins, f"{name}/{cell}: port {p} has no pin glyph")

    def test_toggles_and_offline(self):
        with open(self.out["ibs"][3], encoding="utf-8") as f:
            html = f.read()
        for t in ("wl", "val", "name", "net"):
            self.assertIn(f'data-toggle="{t}"', html)
        self.assertIsNone(re.search(r'<script[^>]+src=', html), "viewer must not load external scripts")

    def _view(self, cell):
        html = self.out["ibs"][3]
        return parse_html(html)[cell]

    def test_verifier_detects_open(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("CTLE")
        v["wires"] = v["wires"][1:]   # delete a wire
        r = check_view(v, ir["cells"]["CTLE"], {})
        self.assertFalse(r["ok"])
        self.assertTrue(any("OPEN" in e or "닿지 않음" in e for e in r["errors"]), r["errors"])

    def test_verifier_detects_short(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("CTLE")
        # draw an extra wire from the INP gate pin to the INN gate pin
        P = {(i, p): (x, y) for i, p, x, y in v["pins"]}
        (x1, y1), (x2, y2) = P[("M1", "g")], P[("M2", "g")]
        v["wires"].append((x1, y1, x1, y1 - 200))
        v["wires"].append((x1, y1 - 200, x2, y1 - 200))
        v["wires"].append((x2, y1 - 200, x2, y2))
        r = check_view(v, ir["cells"]["CTLE"], {})
        self.assertTrue(any("SHORT" in e for e in r["errors"]), r["errors"])

    def test_verifier_detects_text_overlap(self):
        ir = extract_auto_blocks(parse_file(IBS))
        v = self._view("INPUT_BUFFER_SYSTEM")
        w = v["wires"][0]
        v["texts"].append({"txt": "X", "box": text_box("XXXX", (w[0] + w[2]) / 2, w[1] + 3, "middle", 10),
                           "kind": "netlabel", "sym": None})
        r = check_view(v, ir["cells"]["INPUT_BUFFER_SYSTEM"], {})
        self.assertTrue(any("배선과 겹침" in x for x in r["lint"]["warnings"]))


if __name__ == "__main__":
    unittest.main()
