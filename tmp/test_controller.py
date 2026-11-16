from check_controller import *
from functools import lru_cache

c=Circuit('labs/Lab4/CPU/lab4controller.bdf')
# Evaluate the actual Quartus-converted netlist, with OR5 primitive semantics.
v=Path('tmp/controller-verify/lab4controller.v').read_text().split('endmodule')[0]
assigns=dict(re.findall(r'assign\s+(\w+)\s*=\s*([^;]+);',v))
for body in re.findall(r'or5_\d+\s+\w+\((.*?)\);',v,re.S):
    ports=dict(re.findall(r'\.(\w+)\((\w+)\)',body))
    assigns[ports['OUT']]=' | '.join(ports['IN'+str(i)] for i in range(1,6))
@lru_cache(None)
def expand(name):
    if name not in assigns:return name
    return '('+re.sub(r'\b[A-Za-z_]\w*\b',lambda m:expand(m[0]),assigns[name])+')'
fn='def controls('+','.join(c.inputs)+'):\n    return {'+','.join(repr(k)+':('+expand(k)+')&1' for k in c.outputs)+'}'
ns={};exec(fn,ns);control=ns['controls']
def values(ir,t,dr,stop):return {**{f'IR{i}':(ir>>i)&1 for i in range(8)},**{f'DR{i}':(dr>>i)&1 for i in range(8)},**{f'T{i}':int(t==i) for i in range(13)},'Stop':stop}
def run(ir,t,dr=0,stop=0):return control(**values(ir,t,dr,stop))
def select(o,prefix):return sum(o[prefix+str(i)]<<i for i in range(3))

# Independent RTL table oracle: selectors are checked only when consumed.
def expected(ir,t,dr,stop):
    o={k:0 for k in c.outputs if not k.startswith(('BusSel','ALU_Sel'))}; bus=alu=None
    def set_(*names):
        for name in names:o[name]=1
    reg=bool(ir&128); op=ir&63
    if t==0:set_('AR_Load');bus=6
    if t==1:set_('OUTD_Load');bus=0
    if t==2:set_('AR_Load');o['PC_Inc']=int(not stop);bus=2
    if t==3:set_('IR_Load');bus=0
    if t==5:
        if reg:
            set_('SC_Clear')
            if op==1:set_('AC_Clear')
            elif op==16:set_('AC_Inc')
            elif op==32:set_('Halt')
            else:set_('AC_Load');alu={2:7,4:2,8:3}[op]
        else:set_('AR_Load');o['PC_Inc']=int(not stop);bus=2
    if t==6 and not reg:set_('AR_Load');bus=0
    if t==7 and not reg:
        if ir&64:set_('AR_Load');bus=0
        if op==0:set_('DR_Load');bus=1
    if not reg:
        if op==0 and t==8:set_('AC_Load','SC_Clear');alu=6
        if op in (1,2,3,4,32) and t==8:set_('DR_Load');bus=0
        if op in (1,2,3,4) and t==9:set_('AC_Load','SC_Clear');alu={1:4,2:0,3:1,4:6}[op]
        if op==8 and t==9:set_('memwrite','SC_Clear');bus=5
        if op==16 and t==8:set_('PC_Load','SC_Clear');bus=1
        if op==32:
            if t==9:set_('DR_Inc')
            if t==10:set_('memwrite');bus=3
            if t in (11,12):o['PC_Inc']=int(dr==0 and not stop)
            if t==12:set_('SC_Clear')
    return o,bus,alu

opcodes=[mode+op for mode in (0,64) for op in (0,1,2,3,4,8,16,32)]+[128+x for x in (1,2,4,8,16,32)]
count=0
for ir in opcodes:
    for t in range(13):
        for dr in range(256):
            for stop in (0,1):
                o=run(ir,t,dr,stop);e,bus,alu=expected(ir,t,dr,stop)
                assert all(o[k]==v for k,v in e.items()),(ir,t,dr,stop,o,e)
                # Indirect LDD still selects AR for its immediate transfer.
                if bus is not None:assert select(o,'BusSel')==bus,(ir,t,'bus',o,bus)
                if alu is not None:assert select(o,'ALU_Sel')==alu,(ir,t,'alu',o,alu)
                count+=1
print(f'PASS: {count:,} control-table cases (22 opcodes, 13 states, every DR value, both Stop values).')

for ir in range(256):
    for t in range(13):
        for stop in (0,1):
            for dr in (0,1,255):
                inputs=values(ir,t,dr,stop)
                assert c.evaluate(inputs)==control(**inputs),(ir,t,dr,stop)
print('PASS: 19,968 BDF/Quartus-netlist equivalence cases, including all opcode byte values.')

# Clock-step datapath model driven by the converted controller, using the lab MIF.
mem=[0]*256
for a,b,data in re.findall(r'\[([0-9A-F]+)\.\.([0-9A-F]+)\]\s*:\s*([0-9A-F]+)',Path('labs/Lab4/CPU/memorycontents8.mif').read_text()):
    for i in range(int(a,16),int(b,16)+1):mem[i]=int(data,16)
for a,data in re.findall(r'^\s*([0-9A-F]+)\s*:\s*([0-9A-F]+)',Path('labs/Lab4/CPU/memorycontents8.mif').read_text(),re.M):mem[int(a,16)]=int(data,16)
ar=pc=dr=ac=ir=t=stop=0;writes=[]
for cycle in range(10000):
    o=run(ir,t,dr,stop)
    bus=[mem[ar],ar,pc,dr,ir,ac,255,0][select(o,'BusSel')]
    alu=[ac+dr,ac-dr,ac<<1,(ac>>1)|(ac&128),ac&dr,ac|dr,dr,~ac][select(o,'ALU_Sel')]&255
    if o['memwrite']:mem[ar]=bus;writes.append((ar,bus))
    if o['AR_Load']:ar=bus
    if o['PC_Load']:pc=bus
    elif o['PC_Inc']:pc=(pc+1)&255
    if o['DR_Load']:dr=bus
    elif o['DR_Inc']:dr=(dr+1)&255
    if o['IR_Load']:ir=bus
    if o['AC_Clear']:ac=0
    elif o['AC_Load']:ac=alu
    elif o['AC_Inc']:ac=(ac+1)&255
    if o['Halt']:stop=1;break
    t=0 if o['SC_Clear'] else t+1
else:raise AssertionError('Program failed to halt')
assert mem[248:255]==[1,1,2,3,5,8,13],mem[248:255]
assert [d for a,d in writes if a==242]==[2,3,5,8,13]
print(f'PASS: Fibonacci datapath model halted after {cycle+1} steps; F8..FE = {mem[248:255]}; all checker writes matched.')
