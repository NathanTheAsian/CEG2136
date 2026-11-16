from check_controller import *
from copy import deepcopy

path=Path('labs/Lab4/CPU/lab4controller.bdf')
backup=Path('tmp/lab4controller.before.bdf')
source=path.read_text()
if not backup.exists(): backup.write_text(source)
source=backup.read_text()
nodes=parse(source)
templates={kids(n,'text')[0][1]:deepcopy(n) for n in nodes if n[0]=='symbol'}

def serialize(n,indent=0):
    # All atoms may be quoted in BDF except keywords and numeric coordinates.
    def atom(x):
        return x if re.fullmatch(r'-?\d+(?:\.\d+)?',x) else '"'+x+'"'
    parts=['\t'*indent+'('+n[0]]
    for x in n[1:]:
        if isinstance(x,list): parts.append('\n'+serialize(x,indent+1))
        else: parts.append(' '+atom(x))
    return ''.join(parts)+')'

def wire(a,b,name=None):
    n=['connector']
    if name:
        x,y=min(a[0],b[0]),a[1]
        n.append(['text',name,['rect',str(x+4),str(y-16),str(x+4+8*len(name)),str(y-2)],['font','Arial',['font_size','8']]])
    n += [['pt',*map(str,a)],['pt',*map(str,b)]]
    nodes.append(n)
    return n

def gate(typ,name,x,cy):
    n=deepcopy(templates[typ]); r=one(n,'rect')
    op=next(p for p in kids(n,'port') if kids(p,'output'))
    ox,oy=point(one(op,'pt')); width=int(r[3])-int(r[1]); height=int(r[4])-int(r[2]); y=cy-oy
    r[1:]=list(map(str,[x,y,x+width,y+height])); kids(n,'text')[1][1]=name
    nodes.append(n)
    ins=sorted((x+point(one(p,'pt'))[0],y+point(one(p,'pt'))[1]) for p in kids(n,'port') if kids(p,'input'))
    return n,ins,(x+ox,cy)

def replace(name,typ):
    old=next(n for n in nodes if n[0]=='symbol' and kids(n,'text')[1][1]==name)
    x,y=point(one(old,'rect')); op=next(p for p in kids(old,'port') if kids(p,'output')); cy=y+point(one(op,'pt'))[1]
    nodes.remove(old)
    return gate(typ,name,x,cy)

def named_gate(typ,name,x,y,inputs,output):
    _,ins,out=gate(typ,name,x,y)
    for i,(p,label) in enumerate(zip(ins,inputs)):wire((x-160+32*i,p[1]),p,label)
    wire(out,(out[0]+120,out[1]),output)

def augment(output,typ,extras,x,y):
    # Keep the original output pin and its symbol interface unchanged.
    c=Circuit(backup)
    p=c.outputs[output]
    n=next(n for n in nodes if n[0]=='connector' and any(point(pt)==p for pt in kids(n,'pt')))
    a,b=[point(pt) for pt in kids(n,'pt')]; driver=b if a==p else a
    nodes.remove(n)
    wire(driver,(driver[0]+16,driver[1]),output+'_base')
    wire((p[0]-16,p[1]),p,output)
    named_gate(typ,'fix_'+output,x,y,[output+'_base']+extras,output)

# Restore the T2 fetch connection's spelling.
for n in nodes:
    if n[0]=='connector':
        for t in kids(n,'text'):
            if t[1]=='t2':t[1]='T2'

# ALU transfer, complement, AND, and subtraction must select independently.
replace('inst49','OR2')
replace('inst52','OR3')
wire((1520,-88),(1528,-88),'IR1')
replace('inst43','OR2')
nodes[:]=[n for n in nodes if not(n[0]=='connector' and any(point(p)==(1464,-392) for p in kids(n,'pt')))]
old=next(n for n in nodes if n[0]=='symbol' and kids(n,'text')[1][1]=='inst56')
nodes.remove(old)
nodes[:]=[n for n in nodes if not(n[0]=='connector' and any(point(p) in [(1448,64),(1448,80)] for p in kids(n,'pt')))]
wire((1448,72),(1512,72),'Y2')

# Shared LDD transfer term already exists in the ALU selector.
wire((1720,-248),(1736,-248),'LDD_Load')
replace('inst41','OR3')
wire((704,472),(712,472),'LDD_Load')

# Skip only on a zero incremented data word, while execution is running.
named_gate('AND2','fix_skip_enable',520,1120,['DR_zero','Stop_n'],'Skip_PC')
for n in nodes:
    if n[0]=='symbol' and kids(n,'text')[1][1]=='inst24':
        x,y=point(one(n,'rect')); p=next(p for p in kids(n,'port') if kids(p,'output')); a,b=point(one(p,'pt')); wire((x+a,y+b),(x+a+16,y+b),'Stop_n');break
for name,cy in [('inst30',-56),('inst31',8)]:
    replace(name,'AND3');wire((512,cy),(520,cy),'Skip_PC')

# Missing indirect-address, immediate-load, and instruction-end paths.
named_gate('AND2','fix_indirect',520,1232,['T7','X1'],'Indirect_AR')
named_gate('AND2','fix_immediate',520,1344,['T7','Y7'],'Immediate_DR')
named_gate('AND2','fix_register_end',520,1456,['T5','X2'],'Register_End')
augment('AR_Load','OR2',['Indirect_AR'],1056,1120)
augment('DR_Load','OR2',['Immediate_DR'],1056,1232)
augment('SC_Clear','OR3',['Register_End','PC_Load'],1056,1344)

# Preserve original formatting of untouched objects, especially the I/O pins.
starts=[m.start() for m in re.finditer(r'^\(',source,re.M) if m.start()>=source.index('(header')]
raw=source[:starts[0]]
original=parse(source)
original_text={id(n):source[a:b] for n,a,b in zip(original,starts,starts[1:]+[len(source)])}
by_value={repr(n):original_text[id(n)] for n in original}
path.write_text(raw+''.join(by_value.get(repr(n),serialize(n)+'\n') for n in nodes))

