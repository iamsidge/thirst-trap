#!/usr/bin/env python3
"""Generate schematic.svg and stripboard.svg for THIRSTY PLANTS."""
import sys
OUT = sys.argv[1]

INK, MUTE, BG = "#1d1d1f", "#6b6b70", "#ffffff"
FONT = "font-family='DejaVu Sans, Helvetica, Arial, sans-serif'"

# ------------------------------------------------------------------ schematic
s = []
def L(*pts, w=2, c=INK):
    p = " ".join(f"{x},{y}" for x, y in pts)
    s.append(f"<polyline points='{p}' fill='none' stroke='{c}' stroke-width='{w}' stroke-linejoin='round' stroke-linecap='round'/>")
def T(x, y, t, size=14, anchor="middle", c=INK, weight="normal"):
    s.append(f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{c}' text-anchor='{anchor}' font-weight='{weight}'>{t}</text>")
def dot(x, y): s.append(f"<circle cx='{x}' cy='{y}' r='4' fill='{INK}'/>")
def label(x, y, t, side="right"):
    w = 12 + 8.5 * len(t)
    x0 = x if side == "right" else x - w
    s.append(f"<rect x='{x0}' y='{y-11}' width='{w}' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>")
    T(x0 + w/2, y + 5, t, 13, c="#3355aa", weight="bold")
def res_v(x, y1, y2, name, val, side=1):
    m = (y1 + y2) / 2
    L((x, y1), (x, m - 28)); L((x, m + 28), (x, y2))
    s.append(f"<rect x='{x-9}' y='{m-28}' width='18' height='56' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
    a = "start" if side > 0 else "end"
    T(x + side*16, m - 4, name, 13, a, weight="bold"); T(x + side*16, m + 13, val, 13, a, MUTE)
def res_h(x1, x2, y, name, val):
    m = (x1 + x2) / 2
    L((x1, y), (m - 28, y)); L((m + 28, y), (x2, y))
    s.append(f"<rect x='{m-28}' y='{y-9}' width='56' height='18' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
    T(m, y - 16, name + '  ' + val, 13, weight="bold")
def cap_v(x, y1, y2, name, val, polar=False):
    m = (y1 + y2) / 2
    L((x, y1), (x, m - 6)); L((x, m + 6), (x, y2))
    L((x - 18, m - 6), (x + 18, m - 6), w=3)
    if polar:
        s.append(f"<path d='M{x-18},{m+12} Q{x},{m+2} {x+18},{m+12}' fill='none' stroke='{INK}' stroke-width='3'/>")
        T(x - 24, m - 10, "+", 14)
    else:
        L((x - 18, m + 6), (x + 18, m + 6), w=3)
    T(x + 26, m - 2, name, 13, "start", weight="bold"); T(x + 26, m + 15, val, 13, "start", MUTE)

W, H = 1320, 640
VCC, GND = 90, 580

# rails
L((60, VCC), (1290, VCC), w=2.5); L((60, GND), (1290, GND), w=2.5)
T(64, VCC - 12, "+4.5 V", 14, "start", weight="bold"); T(64, GND + 24, "GND (0 V)", 14, "start", weight="bold")

# battery
bx = 90
L((bx, VCC), (bx, 280))
for i, yy in enumerate([280, 306, 332]):
    L((bx - 22, yy), (bx + 22, yy), w=3); L((bx - 11, yy + 10), (bx + 11, yy + 10), w=5)
L((bx, 342), (bx, GND)); dot(bx, VCC); dot(bx, GND)
T(bx + 30, 296, "BT1", 13, "start", weight="bold"); T(bx + 30, 313, "3 × AA", 13, "start", MUTE); T(bx + 30, 330, "4.5 V", 13, "start", MUTE)
T(bx - 30, 286, "+", 15)

# caps
cap_v(190, VCC, GND, "C1", "220 µF", polar=True); dot(190, VCC); dot(190, GND)
cap_v(270, VCC, GND, "C2", "100 nF"); dot(270, VCC); dot(270, GND)
T(230, 470, "next to U1", 12, c=MUTE)

# pots
def pot(x, name, purpose, wl):
    label(x, 170, "PB1", "right") if False else None
    L((x, 200), (x, 260))
    s.append(f"<rect x='{x-9}' y='260' width='18' height='70' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
    L((x, 330), (x, GND)); dot(x, GND)
    # wiper arrow
    L((x + 40, 295), (x + 14, 295))
    s.append(f"<path d='M{x+12},295 l10,-6 l0,12 z' fill='{INK}'/>")
    L((x + 40, 295), (x + 40, 230))
    label(x + 40, 218, wl, "right") if False else None
    s.append(f"<rect x='{x+18}' y='{208}' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>")
    T(x + 40, 224, wl, 13, c="#3355aa", weight="bold")
    s.append(f"<rect x='{x-22}' y='{178}' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>")
    T(x, 194, "PB1", 13, c="#3355aa", weight="bold")
    T(x - 16, 380, name, 13, "end", weight="bold"); T(x - 16, 397, "10k lin", 13, "end", MUTE)
    T(x - 16, 414, purpose, 13, "end", MUTE)
pot(390, "RV1", "EVERY", "PB3")
pot(500, "RV2", "FOR", "PB4")

# ATtiny85
ux0, ux1, uy0, uy1 = 620, 780, 230, 450
s.append(f"<rect x='{ux0}' y='{uy0}' width='{ux1-ux0}' height='{uy1-uy0}' fill='#fafafa' stroke='{INK}' stroke-width='2.5' rx='4'/>")
s.append(f"<path d='M{(ux0+ux1)/2-12},{uy0} a12,12 0 0,0 24,0' fill='none' stroke='{INK}' stroke-width='2'/>")
T((ux0 + ux1)/2, uy0 + 110, "U1", 15, weight="bold"); T((ux0 + ux1)/2, uy0 + 130, "ATtiny85", 14, c=MUTE)
lp = [(1, "PB5/RST", 260), (2, "PB3", 310), (3, "PB4", 360), (4, "GND", 410)]
rp = [(8, "VCC", 260), (7, "PB2", 310), (6, "PB1", 360), (5, "PB0", 410)]
for n, nm, y in lp:
    L((ux0 - 34, y), (ux0, y)); T(ux0 + 8, y + 5, nm, 12, "start"); T(ux0 - 17, y - 6, str(n), 11, c=MUTE)
for n, nm, y in rp:
    L((ux1, y), (ux1 + 34, y)); T(ux1 - 8, y + 5, nm, 12, "end"); T(ux1 + 17, y - 6, str(n), 11, c=MUTE)
# pin 1 NC
L((ux0 - 34 - 7, 253), (ux0 - 34 + 7, 267)); L((ux0 - 34 - 7, 267), (ux0 - 34 + 7, 253))
T(ux0 - 48, 265, "NC", 12, "end", MUTE)
# pins 2,3 labels
s.append(f"<rect x='{ux0-34-48}' y='299' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>"); T(ux0 - 34 - 26, 315, "PB3", 13, c="#3355aa", weight="bold")
s.append(f"<rect x='{ux0-34-48}' y='349' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>"); T(ux0 - 34 - 26, 365, "PB4", 13, c="#3355aa", weight="bold")
# pin 4 to GND
L((ux0 - 34, 410), (ux0 - 50, 410), (ux0 - 50, GND)); dot(ux0 - 50, GND)
# pin 8 to VCC
L((ux1 + 34, 260), (ux1 + 50, 260), (ux1 + 50, VCC)); dot(ux1 + 50, VCC)

# LED branch from pin 6 (PB1)
lx = 900
L((ux1 + 34, 360), (lx, 360)); dot(lx, 360)
s.append(f"<rect x='{lx-22}' y='322' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>"); T(lx, 338, "PB1", 13, c="#3355aa", weight="bold")
L((lx, 344), (lx, 360))
res_v(lx, 360, 470, "R3", "1k", side=-1)
# LED pointing down
s.append(f"<path d='M{lx-14},{470} L{lx+14},{470} L{lx},{494} Z' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
L((lx - 14, 494), (lx + 14, 494), w=2.5)
for dy in (474, 486):
    L((lx + 18, dy), (lx + 32, dy - 10)); s.append(f"<path d='M{lx+32},{dy-10} l-7,1 l4,5 z' fill='{INK}'/>")
L((lx, 494), (lx, GND)); dot(lx, GND)
T(lx - 20, 486, "D2", 13, "end", weight="bold"); T(lx - 20, 503, "LED", 13, "end", MUTE)
T(lx + 8, 530, "ALIVE", 12, "start", MUTE)

# button from pin 7 (PB2)
bx2 = 960
L((ux1 + 34, 310), (bx2, 310), (bx2, 420))
L((bx2, 460), (bx2, GND)); dot(bx2, GND)
s.append(f"<circle cx='{bx2}' cy='420' r='3.5' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
s.append(f"<circle cx='{bx2}' cy='460' r='3.5' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
L((bx2 - 14, 428), (bx2 - 14, 452), w=2.5); L((bx2 - 14, 440), (bx2 - 30, 440))
T(bx2 + 14, 436, "S1", 13, "start", weight="bold"); T(bx2 + 14, 453, "WATER", 13, "start", MUTE)
T(bx2 + 14, 470, "(int. pull-up)", 11, "start", MUTE)

# pin 5 (PB0) -> gate resistor -> MOSFET
L((ux1 + 34, 410), (ux1 + 40, 410))
s.append(f"<rect x='{ux1+40}' y='399' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>"); T(ux1 + 62, 415, "PB0", 13, c="#3355aa", weight="bold")

# Power stage on far right, own block
px = 1150
s.append(f"<rect x='{px-30}' y='520' width='0' height='0'/>")
# R1 220 from PB0 label to gate node
gy = 500
s.append(f"<rect x='{px-120-44}' y='{gy-11}' width='44' height='22' rx='11' fill='#eef3ff' stroke='#3355aa' stroke-width='1.5'/>"); T(px - 142, gy + 5, "PB0", 13, c="#3355aa", weight="bold")
res_h(px - 120, px - 20, gy, "R1", "220 Ω")
# gate node + R2 to GND
gn = px - 40
dot(gn, gy)
# MOSFET symbol (N-channel enhancement)
mx = px + 10
L((px - 20, gy), (mx - 6, gy))
L((mx - 6, gy - 22), (mx - 6, gy + 22), w=2.5)          # gate plate
for yy in (gy - 18, gy, gy + 18):
    L((mx + 2, yy - 7), (mx + 2, yy + 7), w=3)            # channel segments
L((mx + 2, gy - 18), (mx + 28, gy - 18), (mx + 28, 420))  # drain up
L((mx + 2, gy + 18), (mx + 28, gy + 18), (mx + 28, GND))  # source down
L((mx + 2, gy), (mx + 28, gy), (mx + 28, gy + 18))
s.append(f"<path d='M{mx+4},{gy} l10,-5 l0,10 z' fill='{INK}'/>")
dot(mx + 28, GND)
T(mx + 36, gy + 4, "Q1", 13, "start", weight="bold"); T(mx + 36, gy + 21, "IRLZ44N", 12, "start", MUTE)
T(mx - 10, gy - 30, "G", 11, c=MUTE); T(mx + 40, gy - 22, "D", 11, c=MUTE); T(mx + 40, gy + 40, "S", 11, c=MUTE)
# R2 100k gate to GND, drawn below gate node
L((gn, gy), (gn, gy + 6))
s.append(f"<rect x='{gn-8}' y='{gy+6}' width='16' height='40' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
L((gn, gy + 46), (gn, GND)); dot(gn, GND)
T(gn - 14, gy + 26, "R2", 13, "end", weight="bold"); T(gn - 14, gy + 43, "100k", 13, "end", MUTE)

# pump + flyback diode between VCC and drain
dx = mx + 28
L((dx, VCC), (dx, 200)); dot(dx, VCC)
s.append(f"<circle cx='{dx}' cy='250' r='34' fill='{BG}' stroke='{INK}' stroke-width='2.5'/>")
T(dx, 258, "M", 22, weight="bold")
L((dx, 216), (dx, 200)); L((dx, 284), (dx, 420))
T(dx - 44, 246, "M1", 13, "end", weight="bold"); T(dx - 44, 263, "pump", 13, "end", MUTE)
T(dx + 8, 212, "+", 14, "start")
# diode in parallel, cathode to + side
ddx = dx + 70
L((dx, 180), (ddx, 180), (ddx, 236)); dot(dx, 180)
L((dx, 330), (ddx, 330), (ddx, 266)); dot(dx, 330)
s.append(f"<path d='M{ddx-14},{266} L{ddx+14},{266} L{ddx},{240} Z' fill='{BG}' stroke='{INK}' stroke-width='2'/>")
L((ddx - 14, 238), (ddx + 14, 238), w=2.5)
T(ddx + 4, 300, "D1", 13, "start", weight="bold"); T(ddx + 4, 317, "1N5819", 12, "start", MUTE)
T(ddx - 6, 158, "solder across pump", 11, "end", MUTE)

# title + notes
T(W/2, 36, "THIRSTY PLANTS — schematic", 20, weight="bold")
T(W/2, 58, "Blue labels with the same name are the same connection.", 13, c=MUTE)
notes = ["PB1 powers the pots only while they are read, and also drives the LED.",
         "D1 is soldered directly on the pump terminals, stripe (cathode) to the + terminal.",
         "Pump on/off is low-side switched by Q1. Keep C1 + C2 close to U1 pins 8 and 4."]
for i, n in enumerate(notes): T(60, 636 + 18 * i, "• " + n, 12, "start", MUTE)

svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H+50}' width='{W}' height='{H+50}'>"
       f"<rect width='100%' height='100%' fill='{BG}'/>" + "".join(s) + "</svg>")
# shift notes below GND rail
svg = svg.replace(f"height='{H+40}'>", f"height='{H+40}'>", 1)
open(f"{OUT}/schematic.svg", "w").write(svg)

# ------------------------------------------------------------------ stripboard
COLS, ROWS, P = 17, 8, 40           # pitch in px
ox, oy = 90, 120                    # hole (1,1) position
def hp(c, r): return ox + (c - 1) * P, oy + (r - 1) * P
b = []
def B(x): b.append(x)
def bt(x, y, t, size=13, anchor="middle", c=INK, weight="normal"):
    halo = "" if c in ("#fff", "#ddd") else " stroke='#fff' stroke-width='3' paint-order='stroke' stroke-linejoin='round'"
    B(f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{c}' text-anchor='{anchor}' font-weight='{weight}'{halo}>{t}</text>")
SW, SH = 1100, 700
B(f"<rect width='100%' height='100%' fill='{BG}'/>")
bt(SW/2, 36, "THIRSTY PLANTS — stripboard layout (17 × 8 holes, ~45 × 22 mm)", 20, weight="bold")
bt(SW/2, 58, "Viewed from the COMPONENT side. Copper strips run left–right underneath.", 13, c=MUTE)
# board
x0, y0 = hp(1, 1); x1, y1 = hp(COLS, ROWS)
B(f"<rect x='{x0-26}' y='{y0-26}' width='{x1-x0+52}' height='{y1-y0+52}' rx='6' fill='#d8b07a' stroke='#9c7440' stroke-width='2'/>")
cuts = {(8,2),(8,3),(8,4),(8,5),(14,3)}
for r in range(1, ROWS + 1):
    xa, y = hp(1, r); xb, _ = hp(COLS, r)
    B(f"<rect x='{xa-18}' y='{y-13}' width='{xb-xa+36}' height='26' rx='3' fill='#c98a4b' opacity='0.55'/>")
    bt(x0 - 44, y + 5, str(r), 12, c=MUTE)
for c in range(1, COLS + 1):
    x, _ = hp(c, 1); bt(x, y0 - 34, str(c), 12, c=MUTE)
for c in range(1, COLS + 1):
    for r in range(1, ROWS + 1):
        x, y = hp(c, r); B(f"<circle cx='{x}' cy='{y}' r='4.5' fill='#5a3d1c'/>")
# net names on strip ends (right side)
right_net = {1: "+4.5 V", 2: "+4.5 V (pin 8)", 3: "PB2 | LED", 4: "PB1", 5: "PB0", 6: "GATE", 7: "DRAIN", 8: "GND"}
left_net = {1: "+4.5 V", 2: "nc", 3: "PB3", 4: "PB4", 5: "GND", 6: "–", 7: "–", 8: "GND"}
for r in range(1, ROWS + 1):
    x, y = hp(COLS, r); bt(x + 40, y + 5, right_net[r], 12, "start", "#7a4a12")
def lead(c1, r1, c2, r2, col=INK, w=3):
    xa, ya = hp(c1, r1); xb, yb = hp(c2, r2)
    B(f"<line x1='{xa}' y1='{ya}' x2='{xb}' y2='{yb}' stroke='{col}' stroke-width='{w}' stroke-linecap='round'/>")
    for x, y in ((xa, ya), (xb, yb)): B(f"<circle cx='{x}' cy='{y}' r='6' fill='{col}'/>")
# U1 socket
xa, ya = hp(7, 2); xb, yb = hp(10, 5)
B(f"<rect x='{xa-14}' y='{ya-18}' width='{xb-xa+28}' height='{yb-ya+36}' rx='4' fill='#222' opacity='0.92'/>")
B(f"<path d='M{(xa+xb)/2-9},{ya-18} a9,9 0 0,0 18,0' fill='#888'/>")
for i, (c, r) in enumerate([(7,2),(7,3),(7,4),(7,5),(10,5),(10,4),(10,3),(10,2)]):
    x, y = hp(c, r); B(f"<circle cx='{x}' cy='{y}' r='6' fill='#c0c0c0'/>")
    n = i + 1; bt(x + (16 if c == 7 else -16), y + 4, str(n), 11, "middle", "#fff")
bt(xa + 14, ya - 26, "U1", 12, "start", weight="bold")
B(f"<circle cx='{xa+8}' cy='{ya-6}' r='0'/>")
# cuts
for c, r in cuts:
    x, y = hp(c, r)
    B(f"<circle cx='{x}' cy='{y}' r='12' fill='#fff' stroke='#d0021b' stroke-width='3'/>")
    B(f"<line x1='{x-8}' y1='{y-8}' x2='{x+8}' y2='{y+8}' stroke='#d0021b' stroke-width='3'/><line x1='{x-8}' y1='{y+8}' x2='{x+8}' y2='{y-8}' stroke='#d0021b' stroke-width='3'/>")
# jumpers (bare/insulated wire links)
lead(11, 1, 11, 2, "#2b7a2b"); bt(hp(11,1)[0] + 14, hp(11,1)[1] + 26, "J1", 12, "start", "#2b7a2b", "bold")
lead(2, 5, 2, 8, "#2b7a2b"); bt(hp(2,6)[0] + 12, hp(2,6)[1] + 26, "J2", 12, "start", "#2b7a2b", "bold")
# C1 electrolytic lying flat
lead(3, 1, 3, 5, "#555")
xa, ya = hp(3, 2); B(f"<rect x='{xa-15}' y='{ya-6}' width='30' height='88' rx='8' fill='#1f3f7a'/>")
B(f"<rect x='{xa+7}' y='{ya-6}' width='6' height='88' fill='#c9d3e8'/>")
bt(xa, ya + 46, "C1", 12, c="#fff", weight="bold"); bt(xa - 26, ya + 4, "+", 18, c="#d0021b", weight="bold")
# C2 ceramic
lead(5, 1, 5, 5, "#555")
xa, ya = hp(5, 3); B(f"<ellipse cx='{xa}' cy='{ya}' rx='13' ry='16' fill='#e2a33a'/>"); bt(xa, ya + 5, "C2", 11, weight="bold")
# R1 220 (standing hairpin) col 12 rows 5-6
def res_stand(c, r1, r2, name, colr):
    lead(c, r1, c, r2, "#555")
    x, y = hp(c, r1); B(f"<circle cx='{x}' cy='{y}' r='11' fill='{colr}' stroke='#555' stroke-width='2'/>")
    xx, yy = hp(c, r2)
    bt(x + 16, (y + yy)/2 + 5, name, 12, "start", weight="bold")
res_stand(12, 5, 6, "R1 220Ω", "#d9c49a")
res_stand(13, 6, 8, "", "#d9c49a")
x, y = hp(13, 7); bt(x + 14, y + 5, "R2 100k", 12, "start", weight="bold")
res_stand(16, 4, 3, "", "#d9c49a")
x, y = hp(16, 3); bt(x - 14, y - 16, "R3 1k", 12, "end", weight="bold")
# Q1 lying flat, legs at col 11 rows 6-8, body to the left
xa, ya = hp(4, 6); xb, yb = hp(10, 8)
B(f"<rect x='{xa-14}' y='{ya-16}' width='{xb-xa+4}' height='{yb-ya+32}' rx='3' fill='#2a2a2a' opacity='0.93'/>")
B(f"<rect x='{xa-14}' y='{ya-16}' width='34' height='{yb-ya+32}' fill='#b8b8b8' opacity='0.95'/>")
B(f"<circle cx='{xa+3}' cy='{(ya+yb)/2}' r='6' fill='#777'/>")
for r, nm in ((6, "G"), (7, "D"), (8, "S")):
    lead(10, r, 11, r, "#c0c0c0", 3)
    x, y = hp(10, r); bt(x - 8, y + 5, nm, 12, "end", "#fff", "bold")
bt((xa + xb)/2 + 6, (ya + yb)/2 + 5, "Q1 IRLZ44N", 12, c="#fff", weight="bold")
bt((xa + xb)/2 + 6, yb + 38, "lying flat, metal tab UP, legs bent down into column 11", 11, c=MUTE)
# off-board wires
wires = [((17,1), "BATT +", "#d0021b"), ((16,1), "PUMP +", "#d0021b"), ((17,8), "BATT −", "#111"),
         ((17,7), "PUMP −", "#111"), ((15,8), "LID: GND (pots, button, LED −)", "#111"), ((12,3), "LID: button", "#e67e00"),
         ((13,4), "LID: top of both pots", "#8e44ad"), ((17,3), "LID: LED +", "#2e86de"),
         ((1,3), "LID: RV1 wiper", "#16a085"), ((1,4), "LID: RV2 wiper", "#27ae60")]
for (c, r), name, col in wires:
    x, y = hp(c, r)
    B(f"<circle cx='{x}' cy='{y}' r='9' fill='none' stroke='{col}' stroke-width='3.5'/>")
# wire legend
lx, ly = 90, 560
bt(lx, ly - 22, "Wires off the board (solder into the ringed holes)", 14, "start", weight="bold")
for i, ((c, r), name, col) in enumerate(wires):
    xx = lx + (i % 2) * 380; yy = ly + (i // 2) * 22
    B(f"<circle cx='{xx+8}' cy='{yy-4}' r='7' fill='none' stroke='{col}' stroke-width='3'/>")
    bt(xx + 24, yy + 1, f"{name}  →  col {c}, row {r}", 13, "start")
# right-hand notes
nx = 760
notes = ["Steps:", "1  Cut the strips at the 5 red ✕ holes", "    (a 3.5 mm drill bit twisted by hand).",
         "    Remember: from the copper side the", "    board is mirrored left↔right.",
         "2  Fit J1, J2, then R1–R3, C2, C1.", "3  Socket for U1, notch towards row 1.",
         "4  Q1 last, flat over rows 6–8.", "5  Off-board wires; D1 goes on the pump.",
         "6  Continuity-test strips before the chip", "    goes in. Check pin 8–pin 4 isn't a short."]
for i, n in enumerate(notes):
    bt(nx, 540 + i * 18 - 12, n, 12 if i else 14, "start", INK if i == 0 else MUTE, "bold" if i == 0 else "normal")
bt(hp(1,1)[0] - 44, y0 - 34, "row", 11, c=MUTE)
open(f"{OUT}/stripboard.svg", "w").write(
    f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {SW} {SH+40}' width='{SW}' height='{SH+40}'>" + "".join(b) + "</svg>")
print("ok")
