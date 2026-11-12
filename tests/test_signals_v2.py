"""v2: signal classification + same-role merging.  python3 -m unittest tests.test_signals_v2 -v"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, "hspice-schematic-v2", "scripts")
if V2 not in sys.path:
    sys.path.insert(0, V2)

import importlib  # noqa: E402

# make sure we load the v2 package even if the v1 'hsch' was imported first
for m in [k for k in sys.modules if k == "hsch" or k.startswith("hsch.")]:
    del sys.modules[m]
sys.path.remove(V2)
sys.path.insert(0, V2)
analyze = importlib.import_module("hsch.analyze")
parser = importlib.import_module("hsch.parser")
signals = importlib.import_module("hsch.signals")

NET = os.path.join(ROOT, "tests", "netlists", "rx_afe_top.sp")


class TestSignalsV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ir = analyze.extract_auto_blocks(parser.parse_file(NET))
        cls.cls = signals.classify_signals(cls.ir)
        for m in [k for k in sys.modules if k == "hsch" or k.startswith("hsch.")]:
            del sys.modules[m]      # leave v1 importable for the other test module

    def assertClass(self, cell, nets, want):
        for n in nets:
            self.assertEqual(self.cls[cell].get(n), want, f"{cell}.{n}")

    def test_top_level_classes(self):
        top = "RX_AFE_TOP"
        self.assertClass(top, ["RX_INP", "RX_INN", "DOUT_EVEN_P", "DOUT_ODD_N", "VGA_P", "CTLE1_P", "E_T2P"], "hs")
        self.assertClass(top, ["CLK_INP", "CLKI", "CLKIB", "CLKQ"], "clk")
        self.assertClass(top, ["C0", "C2", "R1", "G0", "G3", "W1_0", "W4_3"], "ctrl")
        self.assertClass(top, ["IREF", "VBN", "VBP"], "bias")
        self.assertClass(top, ["VDD", "VSS"], "power")

    def test_leaf_classes(self):
        self.assertClass("IDAC_4BIT", ["B0", "B3"], "ctrl")
        self.assertClass("IDAC_4BIT", ["VBN"], "bias")
        self.assertClass("VGA_STAGE", ["G0", "G1"], "ctrl")
        self.assertClass("VGA_STAGE", ["VBN", "VBP"], "bias")
        self.assertClass("CTLE_STAGE", ["C0", "R2"], "ctrl")
        self.assertClass("CTLE_STAGE", ["INP", "OUTN"], "hs")
        self.assertClass("NAND2", ["A", "B", "Y"], "hs")           # CMOS logic inputs, not bias
        self.assertClass("BIAS_GEN", ["IREF_IN", "VBN", "VBP"], "bias")
        self.assertClass("CML_LATCH", ["CLK", "CLKB"], "clk")
        self.assertClass("CLK_DIST_TREE__AUTO1", ["B1P", "B1N"], "clk")   # feeds clock pins only

    def merges(self, cell):
        return {g["name"]: g for g in signals.find_slices(self.ir["cells"][cell])}

    def test_merges(self):
        m = self.merges("VGA_STAGE")
        for n in ("M_G<0:3>_P", "M_G<0:3>_N", "MS_G<0:3>", "MB_G<0:3>"):
            self.assertIn(n, m)
        self.assertEqual(m["MS_G<0:3>"]["pins"], {"d": "T_G<0:3>", "g": "G<0:3>", "s": "B_G<0:3>"})
        m = self.merges("IDAC_4BIT")
        self.assertEqual(set(m), {"MB<0:3>", "MS<0:3>"})
        m = self.merges("CTLE_STAGE")
        self.assertIn("MR<0:2>", m)
        par = [g for g in m.values() if g["kind"] == "parallel"]
        self.assertEqual(len(par), 1)
        self.assertEqual(set(par[0]["members"]), {"C_DEG_BASE", "C0_CAP", "C1_CAP", "C2_CAP"})
        self.assertNotIn("C<0:2>_CAP", m)                           # absorbed by the parallel group
        m = self.merges("DFE_SUMMER")
        self.assertEqual(m["X_DAC<1:4>"]["pins"]["B0"], "W<1:4>_0")
        # chains / differential halves must NOT be merged
        self.assertEqual(self.merges("STRONGARM_SLICER__AUTO0"), {})
        self.assertEqual(self.merges("HALF_RATE_DFE_SLICE"), {})     # X_DFF2 -> X_DFF3 is a shift chain
        self.assertEqual(self.merges("CLK_DIST_TREE"), {})

    def test_expand_check_catches_errors(self):
        sys.path.insert(0, V2)
        for m in [k for k in sys.modules if k == "hsch" or k.startswith("hsch.")]:
            del sys.modules[m]
        collapse = importlib.import_module("hsch.collapse")
        sig = importlib.import_module("hsch.signals")
        vir, vcls, pb, _ = collapse.build_view_ir(self.ir, sig.classify_signals(self.ir))
        for c in self.ir["cells"]:
            self.assertEqual(collapse.expand_check(vir["cells"][c], self.ir["cells"][c], pb), [], c)
        import copy
        bad = copy.deepcopy(vir["cells"]["VGA_STAGE"])
        d = next(x for x in bad["devices"] if x["name"] == "MS_G<0:3>")
        d["pins"] = [[p, ("B_G<3:0>" if p == "s" else n)] for p, n in d["pins"]]   # reversed bus order
        errs = collapse.expand_check(bad, self.ir["cells"]["VGA_STAGE"], pb)
        self.assertTrue(any("MS_G0" in e for e in errs), errs)
        for m in [k for k in sys.modules if k == "hsch" or k.startswith("hsch.")]:
            del sys.modules[m]

    def test_v2_build_rx_afe_end_to_end(self):
        import json
        import subprocess
        import tempfile
        out = tempfile.mkdtemp()
        r = subprocess.run([sys.executable, os.path.join(V2, "build.py"), NET, "-o", os.path.join(out, "rx.html"),
                            "--report", os.path.join(out, "rx.json")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        with open(os.path.join(out, "rx.json")) as f:
            rep = json.load(f)
        self.assertTrue(rep["ok"])
        self.assertEqual(len(rep["views"]), 21)
        for cell, v in rep["views"].items():
            self.assertTrue(v["ok"] and v["expand_ok"], (cell, v["errors"]))
        with open(os.path.join(out, "rx.html"), encoding="utf-8") as f:
            html = f.read()
        self.assertIn('data-toggle="ctrl"', html)
        self.assertIn("MS_G&lt;0:3&gt;", html)            # merged device drawn once
        self.assertIn('class="wire bus', html)               # bus nets thick
        self.assertIn('class="wire clk', html)               # clocks thick

    def test_bus_names(self):
        b = signals.bus_name
        self.assertEqual(b(["T_G0", "T_G1", "T_G2", "T_G3"]), "T_G<0:3>")
        self.assertEqual(b([f"W{a}_{c}" for a in range(1, 5) for c in range(4)]), "W<1:4>_<0:3>")
        self.assertEqual(b(["B0", "B2", "B5"]), "B<0,2,5>")


if __name__ == "__main__":
    unittest.main()
