# Stripboard connectivity check: 17 cols x 8 rows, horizontal strips.
COLS, ROWS = 17, 8
cuts = {(8,2),(8,3),(8,4),(8,5),(14,3)}
pins = {
 'U1.1':(7,2),'U1.2':(7,3),'U1.3':(7,4),'U1.4':(7,5),'U1.8':(10,2),'U1.7':(10,3),'U1.6':(10,4),'U1.5':(10,5),
 'J1.a':(11,1),'J1.b':(11,2),'J2.a':(2,5),'J2.b':(2,8),
 'C1.+':(3,1),'C1.-':(3,5),'C2.a':(5,1),'C2.b':(5,5),
 'R220.a':(12,5),'R220.b':(12,6),'R100k.a':(13,6),'R100k.b':(13,8),
 'Q1.G':(11,6),'Q1.D':(11,7),'Q1.S':(11,8),'R1k.a':(16,4),'R1k.b':(16,3),
 'W.BATT+':(17,1),'W.PUMP+':(16,1),'W.BATT-':(17,8),'W.PUMP-':(17,7),'W.LID_GND':(15,8),
 'W.LID_PB2':(12,3),'W.LID_PB1':(13,4),'W.LID_LED':(17,3),'W.LID_PB3':(1,3),'W.LID_PB4':(1,4)}
jumpers=[('J1.a','J1.b'),('J2.a','J2.b')]
# holes used once
from collections import Counter
c=Counter(pins.values()); assert all(v==1 for v in c.values()), [k for k,v in c.items() if v>1]
assert not (set(pins.values()) & cuts)
def seg(col,row):
    lo=col
    while lo>1 and (lo-1,row) not in cuts: lo-=1
    if (lo,row) in cuts: lo+=1
    return (row,lo)
parent={}
def f(x):
    parent.setdefault(x,x)
    while parent[x]!=x: x=parent[x]
    return x
def u(a,b): parent[f(a)]=f(b)
for p,(cc,r) in pins.items(): u(p,seg(cc,r))
for a,b in jumpers: u(a,b)
nets={}
for p in pins: nets.setdefault(f(p),[]).append(p)
want = {
 'VCC':{'U1.8','C1.+','C2.a','W.BATT+','W.PUMP+'},
 'GND':{'U1.4','C1.-','C2.b','R100k.b','Q1.S','W.BATT-','W.LID_GND'},
 'PB0':{'U1.5','R220.a'},'GATE':{'R220.b','R100k.a','Q1.G'},'DRAIN':{'Q1.D','W.PUMP-'},
 'PB1':{'U1.6','R1k.a','W.LID_PB1'},'LED':{'R1k.b','W.LID_LED'},'PB2':{'U1.7','W.LID_PB2'},
 'PB3':{'U1.2','W.LID_PB3'},'PB4':{'U1.3','W.LID_PB4'},'NC':{'U1.1'}}
got=[{p for p in v if not p.startswith('J')} for v in nets.values()]
ok=True
for n,s in want.items():
    if s not in got: ok=False; print('MISMATCH',n,s)
print('extra nets:', [g for g in got if g not in want.values()])
print('ALL NETS OK' if ok else 'FAIL')
