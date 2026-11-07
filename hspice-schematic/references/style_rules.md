# Schematic style rules (textbook / Razavi style)

Extracted from reference figures supplied by the user (merged CTLE + DFE summer,
source-degenerated CTLE, wireline transceiver block diagram) plus Razavi
conventions. The layout engine implements every rule marked **[auto]**; rules
marked **[lint]** are checked by `verify.py`.

## Transistor level

1. **Mirror symmetry** [auto][lint] – every differential pair (σ-matched devices:
   `INP/INN`, `OUTP/OUTN`, `SP/SN`, … propagated through equal-size devices) is drawn
   as an exact mirror image about a vertical axis. When the whole cell is
   symmetric (each band has at most one self-symmetric device), the axis is global
   (CTLE, CML latch); otherwise each pair is mirrored about its own centred tail
   (merged CTLE/DFE summer: main pair + tap pairs side by side).
2. **Matched siblings are mirrored** [auto] – two equal devices sharing a source node
   (clock pair, tap pair, tail pair) are placed symmetrically around the device that
   feeds them, gates mirrored.
3. **Gate facing** [auto] – input pairs face *outward* (IN on the left, IN̄ on the right);
   cross-coupled and shared-gate pairs face *inward*. Cross-coupled gates are wired
   with two diagonal lines forming an "X" on the axis.
4. **Vertical order** [auto][lint] – supply rail on top, ground at the bottom, PMOS
   above NMOS, loads directly above the drains they feed, tail current source centred
   below the pair it feeds.
5. **One straight horizontal per node** [auto] – drain/source nodes are drawn as a
   single horizontal bus with vertical drops; when two buses overlap at the same
   height the second one is offset by one track (e.g. the two summer output buses).
6. **Degeneration** [auto] – passives between the two source nodes of a pair are drawn
   horizontally between the columns, R above C, with dots at the four junctions.
7. **MOSFET symbol** [auto] – 3-terminal; thick channel line that ends exactly at the
   drain/source stubs; gate plate separated from the channel by a clearly visible
   gate-oxide gap (Razavi proportions: body 21 px wide × 30 px tall, oxide gap 9 px on a
   10 px grid); arrow on the source stub pointing away from the channel (NMOS) / into the
   channel (PMOS); drain and source leave vertically.
8. **Rails** [auto] – VDD is one horizontal rail with the name centred above it; every
   ground connection gets its own ground symbol.
9. **Pin names** [auto] – single-pin inputs (IN, IN̄, H1, CLK, VBIAS) are plain text at
   the end of the gate lead, no terminal circle.
10. **Junctions** [auto][lint] – a dot at every T junction, never a 4-way junction,
    crossings without dots only.
11. **Annotations** [auto] – device name, W/L and m next to the device on the side
    opposite the gate; each class can be toggled off in the viewer.

## Block level

12. **Signal flow** [auto] – left to right; inputs enter on the left with an arrowhead,
    outputs leave on the right; feedback inputs enter from below.
13. **Clock** [auto] – clocks enter from below, straight up into the clock pin.
14. **Bias** [auto] – bias pins are short stubs with the net name; no long bias wires.
15. **Symbols** [auto] – differential amplifier/CTLE = triangle with +/− marks;
    summer = circle with Σ; latch / flip-flop = box (flip-flop clock marked with ▷);
    anything else = box with the cell name.
16. **No overlapping text** [lint] – no label may overlap another label, a wire or a
    symbol outline. The instance label goes to the free side of the symbol.
