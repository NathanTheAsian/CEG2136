import re
from pathlib import Path

def parse(s):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', re.sub(r'/\*.*?\*/', '', s, flags=re.S))
    stack=[[]]
    for t in tokens:
        if t=='(': stack.append([])
        elif t==')':
            n=stack.pop(); stack[-1].append(n)
        else: stack[-1].append(t.strip('"'))
    return stack[0]
def kids(n,k): return [x for x in n if isinstance(x,list) and x[0]==k]
def one(n,k): return kids(n,k)[0]
def point(n): return tuple(map(int,n[1:3]))

class Circuit:
    def __init__(self,path):
        self.nodes=parse(Path(path).read_text()); self.parent={}; self.labels={}; self.gates=[]; self.inputs={}; self.outputs={}
        def root(p):
            self.parent.setdefault(p,p)
            if self.parent[p]!=p: self.parent[p]=root(self.parent[p])
            return self.parent[p]
        self.root=root
        def join(a,b): self.parent[root(a)]=root(b)
        for n in self.nodes:
            if n[0]=='connector':
                pts=[point(p) for p in kids(n,'pt')]
                for p in pts: join(pts[0],p)
                for t in kids(n,'text'): join(pts[0],t[1]); self.labels[t[1]]=pts[0]
            if n[0] in ('pin','symbol'):
                x,y=point(one(n,'rect'))
                if n[0]=='pin':
                    a,b=point(one(n,'pt')); p=(x+a,y+b); name=kids(n,'text')[1][1]; join(p,name)
                    (self.inputs if kids(n,'input') else self.outputs)[name]=p
                else:
                    ports=[]
                    for port in kids(n,'port'):
                        a,b=point(one(port,'pt')); ports.append((bool(kids(port,'output')),(x+a,y+b)))
                    self.gates.append((kids(n,'text')[0][1],kids(n,'text')[1][1],[p for o,p in ports if not o],[p for o,p in ports if o]))
        points=[p for p in self.parent if isinstance(p,tuple)]
        for n in self.nodes:
            if n[0]!='connector':continue
            a,b=[point(p) for p in kids(n,'pt')]
            for p in points:
                if (b[0]-a[0])*(p[1]-a[1])==(b[1]-a[1])*(p[0]-a[0]) and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]):join(a,p)
        self.drivers={}
        for name,p in self.inputs.items(): self.drivers[root(p)]=name
        for typ,name,ins,outs in self.gates:
            for p in outs: self.drivers[root(p)]=(typ,name,ins)
    def expr(self,p,seen=()):
        r=self.root(p)
        if r in seen: return 'LOOP'
        d=self.drivers.get(r)
        if d is None: return 'UNDRIVEN'+str(p)
        if isinstance(d,str): return d
        typ,name,ins=d
        return typ+'('+','.join(self.expr(p,seen+(r,)) for p in ins)+')'
    def evaluate(self,values):
        memo={self.root(k):v for k,v in values.items()}
        def ev(p):
            r=self.root(p)
            if r in memo:return memo[r]
            d=self.drivers[r]
            if isinstance(d,str):raise ValueError(d)
            typ,_,ins=d; v=[ev(i) for i in ins]
            if typ=='NOT': z=not v[0]
            elif typ.startswith('AND'): z=all(v)
            elif typ.startswith('OR'): z=any(v)
            elif typ.startswith('NOR'): z=not any(v)
            elif typ=='VCC':z=True
            elif typ=='GND':z=False
            else:raise ValueError(typ)
            memo[r]=int(z); return int(z)
        return {k:ev(p) for k,p in self.outputs.items()}

if __name__=='__main__':
    c=Circuit('labs/Lab4/CPU/lab4controller.bdf')
    for k,p in c.outputs.items(): print(k,'=',c.expr(p))
    for k,p in c.labels.items():
        if k.startswith(('X','Y','DR')):print(k,'=',c.expr(p))
