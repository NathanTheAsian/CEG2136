import re
from pathlib import Path

def parse(t):
 tokens=re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+',re.sub(r'/\*.*?\*/','',t,flags=re.S));pos=0
 def one():
  nonlocal pos
  v=tokens[pos];pos+=1
  if v!='(':return v.strip('"')
  a=[]
  while tokens[pos]!=')':a.append(one())
  pos+=1;return a
 out=[]
 while pos<len(tokens):out.append(one())
 return out

def fs(x,k):return [v for v in x if isinstance(v,list) and v and v[0]==k]
def f(x,k):return fs(x,k)[0]
def pt(x):return tuple(map(int,f(x,'pt')[1:]))
def inspect(p):
 blocks=parse(p.read_text());parents={};labels={};pins=[];gates=[]
 def root(a):
  parents.setdefault(a,a)
  if parents[a]!=a:parents[a]=root(parents[a])
  return parents[a]
 def union(a,b):parents[root(a)]=root(b)
 for b in blocks:
  if b[0]=='connector':
   pts=[tuple(map(int,v[1:])) for v in fs(b,'pt')];union(*pts)
   for v in fs(b,'text'):
    if not v[1].startswith('<<'):union(pts[0],v[1])
 for b in blocks:
  if b[0] not in ('pin','symbol'):continue
  rect=list(map(int,f(b,'rect')[1:]));texts=fs(b,'text');name=texts[1][1]
  loc=lambda v:(rect[0]+pt(v)[0],rect[1]+pt(v)[1])
  if b[0]=='pin':
   pos=loc(b);pins.append((name,'input' if fs(b,'input') else 'output'));labels.setdefault(root(pos),[]).append(name)
  else:
   ports=[]
   for v in fs(b,'port'):
    pn=f(v,'text')[1];pos=loc(v);ports.append((pn,root(pos)))
    if fs(v,'output'):labels.setdefault(root(pos),[]).append(name+'.'+pn)
   gates.append((texts[0][1],name,ports))
 for kind,name,ports in gates:print(kind,name,{pn:'/'.join(labels.get(root(pos),[str(pos)])) for pn,pos in ports})
 return pins
if __name__=='__main__':
 for p in Path('../../').rglob('*.bdf'):
  if 'simulation' in p.parts:continue
  print('\nFILE',p);print('PINS',inspect(p))
