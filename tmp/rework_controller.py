"""Correct the original gates without adding any symbol instances."""
from check_controller import *
from copy import deepcopy

path=Path('labs/Lab4/CPU/lab4controller.bdf')
previous=Path('tmp/lab4controller.with-added-gates.bdf')
if not previous.exists():previous.write_bytes(path.read_bytes())
source=Path('tmp/lab4controller.before.bdf').read_text()
c=Circuit('tmp/lab4controller.before.bdf')
nodes=parse(source)
original=deepcopy(nodes)
symbols={kids(n,'text')[1][1]:n for n in nodes if n[0]=='symbol'}
templates={kids(n,'text')[0][1]:deepcopy(n) for n in symbols.values()}
templates['AND4']=next(n for n in parse(Path('C:/altera/13.0sp1/quartus/libraries/primitives/logic/and4.bsf').read_text()) if n[0]=='symbol')
gates={g[1]:g for g in c.gates}

# Name each existing electrical net so it can be shared without extra gates.
names={c.root(g[3][0]):'net_'+g[1] for g in c.gates}
for label,p in c.labels.items():names[c.root(p)]=label
for label,p in {**c.inputs,**c.outputs}.items():names[c.root(p)]=label
for name,label in [('inst48','LDD_Load'),('inst67','Immediate_DR'),('inst38','Register_Exec')]:names[c.root(gates[name][3][0])]=label
names[c.root('t2')]='T2'
def net(p):return names[c.root(p)]
def oldins(name):return [net(p) for p in gates[name][2]]
def oldout(name):return net(gates[name][3][0])

# (gate type, input nets, output net, optional replacement position).
changes={
    'inst19':('OR5',oldins('inst19')+['Indirect_AR'],oldout('inst19'),None),
    'inst30':('AND4',['T11','Y6','DR_zero','Stop_n'],oldout('inst30'),None),
    'inst31':('AND4',['T12','Y6','DR_zero','Stop_n'],oldout('inst31'),(520,24)),
    'inst32':('OR2',['Memory_DR','Immediate_DR'],oldout('inst32'),None),
    'inst41':('OR3',oldins('inst41')+['LDD_Load'],oldout('inst41'),None),
    'inst43':('OR2',['Y0','Y3'],oldout('inst43'),None),
    'inst49':('OR2',oldins('inst49'),oldout('inst49'),None),
    'inst52':('OR3',['IR1','IR2','IR3'],oldout('inst52'),None),
    'inst53':('OR3',[oldout('inst50'),oldout('inst51'),'LDD_Load'],oldout('inst53'),None),
    # Reuse the duplicate T8.Y7 gate for indirect fetching.
    'inst54':('AND2',['T7','X1'],'Indirect_AR',(1040,-352)),
    'inst55':('AND2',['Y2','T9'],oldout('inst55'),None),
    # Reuse the incorrect ADD/SUB OR gate for the DR memory-read term.
    'inst56':('AND2',[oldout('inst33'),'T8'],'Memory_DR',(824,64)),
    'inst76':('OR5',oldins('inst76')+['Register_Exec','PC_Load'],oldout('inst76'),None),
}

# Detach physical wire runs touching edited gates, keeping remote named nets.
connectors=[n for n in nodes if n[0]=='connector']
parent={}
def root(p):
    parent.setdefault(p,p)
    if parent[p]!=p:parent[p]=root(parent[p])
    return parent[p]
def join(a,b):parent[root(a)]=root(b)
boundaries=[]
for name,g in gates.items():
    for p in g[2]:boundaries.append((p,False,name))
    for p in g[3]:boundaries.append((p,True,name))
for label,p in c.inputs.items():boundaries.append((p,True,None))
for label,p in c.outputs.items():boundaries.append((p,False,None))
for p,_,_ in boundaries:root(p)
for n in connectors:
    a,b=[point(p) for p in kids(n,'pt')];join(a,b)
for n in connectors:
    a,b=[point(p) for p in kids(n,'pt')]
    for p in list(parent):
        if (b[0]-a[0])*(p[1]-a[1])==(b[1]-a[1])*(p[0]-a[0]) and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]):join(a,p)
touched={root(p) for p,_,name in boundaries if name in changes}
nodes[:]=[n for n in nodes if not (n[0]=='connector' and root(point(one(n,'pt'))) in touched)]

def wire(a,b,label):
    # Compact named stubs avoid introducing long crossing wires.
    x,y=min(a[0],b[0]),a[1]
    nodes.append(['connector',['text',label,['rect',str(x),str(y-14),str(x+6*len(label)),str(y-3)],['font','Arial',['font_size','6']]],['pt',*map(str,a)],['pt',*map(str,b)]])
def stub(p,output,label):
    q=(p[0]+16 if output else p[0]-16,p[1]);wire(p,q,label)
for p,output,name in boundaries:
    if name not in changes and root(p) in touched:stub(p,output,net(p))

for name,(typ,inputs,output,pos) in changes.items():
    old=symbols[name];x,y=point(one(old,'rect'));cy=gates[name][3][0][1]
    if pos:x,cy=pos
    new=deepcopy(templates[typ]);r=one(new,'rect')
    width=int(r[3])-int(r[1]);height=int(r[4])-int(r[2])
    op=next(p for p in kids(new,'port') if kids(p,'output'));ox,oy=point(one(op,'pt'));y=cy-oy
    r[1:]=list(map(str,[x,y,x+width,y+height]));kids(new,'text')[1][1]=name
    nodes[nodes.index(old)]=new
    ins=sorted((x+point(one(p,'pt'))[0],y+point(one(p,'pt'))[1]) for p in kids(new,'port') if kids(p,'input'))
    for p,label in zip(ins,inputs):stub(p,False,label)
    stub((x+ox,cy),True,output)

for name,label in [('inst48','LDD_Load'),('inst67','Immediate_DR'),('inst38','Register_Exec')]:
    p=gates[name][3][0]
    # Label an existing wire at the shared source; preserve its local routing.
    n=next(n for n in nodes if n[0]=='connector' and p in [point(t) for t in kids(n,'pt')])
    if not kids(n,'text'):
        n.insert(1,['text',label,['rect',str(p[0]+4),str(p[1]-14),str(p[0]+4+6*len(label)),str(p[1]-3)],['font','Arial',['font_size','6']]])

for n in nodes:
    if n[0]=='connector':
        for t in kids(n,'text'):
            if t[1]=='t2':t[1]='T2'

def serialize(n,indent=0):
    def atom(x):return x if re.fullmatch(r'-?\d+(?:\.\d+)?',x) else '"'+x+'"'
    # Compact nested graphical primitives, matching Quartus's own format.
    if not any(isinstance(x,list) and any(isinstance(y,list) for y in x[1:]) for x in n[1:]):
        return '\t'*indent+'('+n[0]+''.join((' '+serialize(x).strip()) if isinstance(x,list) else ' '+atom(x) for x in n[1:])+')'
    return '\t'*indent+'('+n[0]+''.join(('\n'+serialize(x,indent+1)) if isinstance(x,list) else ' '+atom(x) for x in n[1:])+ '\n'+'\t'*indent+')'

starts=[m.start() for m in re.finditer(r'^\(',source,re.M) if m.start()>=source.index('(header')]
raws={repr(n):source[a:b] for n,a,b in zip(original,starts,starts[1:]+[len(source)])}
assert [n for n in nodes if n[0]=='pin']==[n for n in original if n[0]=='pin']
assert sorted(kids(n,'text')[1][1] for n in nodes if n[0]=='symbol')==sorted(symbols)
path.write_text(source[:starts[0]]+''.join(raws.get(repr(n),serialize(n)+'\n') for n in nodes))
print(f'Updated {len(changes)} existing gates. Symbol count remains {len(symbols)}; original I/O pins preserved.')
