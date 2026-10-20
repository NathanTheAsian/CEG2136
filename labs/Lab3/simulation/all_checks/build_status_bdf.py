from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]

def blocks(path,kind):
 t=path.read_text();out=[]
 for m in re.finditer(r'^\('+kind+r'\s',t,re.M):
  start=m.start();depth=0;quoted=False
  for i in range(start,len(t)):
   c=t[i]
   if c=='"':quoted=not quoted
   if not quoted:depth+=(c=='(')-(c==')')
   if depth==0:out.append(t[start:i+1]);break
 return out

def move(b,x,y):
 m=re.search(r'\(rect (-?\d+) (-?\d+) (-?\d+) (-?\d+)\)',b);a,c,d,e=map(int,m.groups())
 return b[:m.start()]+f'(rect {x} {y} {x+d-a} {y+e-c})'+b[m.end():]
def instance(b,name):
 hits=list(re.finditer(r'\(text "([^"]*)"',b));m=hits[1];return b[:m.start(1)]+name+b[m.end(1):]
def named_wire(a,b,name):
 x,y=a
 return f'(connector\n (text "{name}" (rect {min(x,b[0])+3} {y-16} {min(x,b[0])+3+8*len(name)} {y-4})(font "Arial" ))\n (pt {a[0]} {a[1]})\n (pt {b[0]} {b[1]})\n)'
def gate(b,x,y,name,nets):
 b=move(instance(b,name),x,y);out=[b]
 for port in blocks_from_string(b,'port'):
  pn=re.search(r'\(text "([^"]*)"',port).group(1);a,c=map(int,re.search(r'\(pt (\d+) (\d+)\)',port).groups());p=(x+a,y+c)
  isout='(output)' in port
  # Horizontal signal stubs except DFF asynchronous controls.
  if pn in ('CLRN','PRN'):
   q=(p[0],p[1]+(24 if pn=='CLRN' else -24))
  else:q=(p[0]+(64 if isout else -80),p[1])
  out.append(named_wire(p,q,nets[pn]))
 return out

def blocks_from_string(t,kind):
 out=[]
 for m in re.finditer(r'\('+kind+r'\s',t):
  start=m.start();depth=0;quoted=False
  for i in range(start,len(t)):
   c=t[i]
   if c=='"':quoted=not quoted
   if not quoted:depth+=(c=='(')-(c==')')
   if depth==0:out.append(t[start:i+1]);break
 return out
prims={}
for p in [ROOT/'Arithmetic/FAddr.bdf',ROOT/'Tools/FourOneMUX.bdf',ROOT/'Tools/4bitRegister.bdf',ROOT/'Arithmetic/1bitArithmeticCircuit.bdf']:
 for b in blocks(p,'symbol'):
  name=re.search(r'\(text "([^"]*)"',b).group(1)
  if name not in prims:prims[name]=b
pins=blocks(ROOT/'Arithmetic/FAddr.bdf','pin');pin_in=next(b for b in pins if '(input)' in b);pin_out=next(b for b in pins if '(output)' in b)
def pin(name,direction,x,y,net=None):
 b=move(instance(pin_in if direction=='input' else pin_out,name),x,y-8)
 start=(x+168,y) if direction=='input' else (x,y)
 end=(start[0]+64,y) if direction=='input' else (x-80,y)
 return [b,named_wire(start,end,net or name)]
header='(header "graphic" (version "1.4"))\n'
inputs=['F3','F2','F1','F0','S3','CAR2','CAR3']
out=[]
for i,name in enumerate(inputs):out+=pin(name,'input',32,64+48*i)
for i,(name,net) in enumerate([('N','F3'),('Z','zero_flag'),('V','overflow_flag'),('Cy','carry_flag')]):out+=pin(name,'output',1104,80+96*i,net)
out+=gate(prims['OR4'],480,32,'result_or',{'IN1':'F3','IN2':'F2','IN3':'F1','IN4':'F0','OUT':'any_result'})
out+=gate(prims['NOT'],736,48,'zero_not',{'IN':'any_result','OUT':'zero_flag'})
out+=gate(prims['NOT'],480,176,'arithmetic_mode',{'IN':'S3','OUT':'arithmetic'})
out+=gate(prims['XOR'],480,272,'carry_difference',{'IN1':'CAR2','IN2':'CAR3','OUT':'carry_xor'})
out+=gate(prims['AND2'],736,240,'overflow_gate',{'IN1':'arithmetic','IN2':'carry_xor','OUT':'overflow_flag'})
out+=gate(prims['AND2'],736,352,'carry_gate',{'IN1':'arithmetic','IN2':'CAR3','OUT':'carry_flag'})
(ROOT/'Tools/state4bit.bdf').write_text(header+'\n'.join(out)+'\n')
# The wrapper uses the existing generated state4bit interface plus four DFFs.
symbol=blocks(ROOT/'state4bit.bsf','symbol')[0]
out=[]
for i,name in enumerate(inputs+['CLK','CLRN']):out+=pin(name,'input',32,64+48*i)
nets={name:name for name in inputs};nets.update({name:'next_'+name for name in ['V','Z','N','Cy']})
out+=gate(symbol,400,64,'status_logic',nets)
for i,name in enumerate(['V','Z','N','Cy']):
 y=64+144*i
 out+=gate(prims['DFF'],800,y,'flag_'+name,{'D':'next_'+name,'CLK':'CLK','CLRN':'CLRN','PRN':'preset_inactive','Q':'stored_'+name})
 out+=pin(name,'output',1024,y+24,'stored_'+name)
# Explicitly tie all active-low presets inactive.
vcc=prims['VCC'];out+=gate(vcc,480,528,'preset_high',{'1':'preset_inactive'})
(ROOT/'Tools/state4bit_register.bdf').write_text(header+'\n'.join(out)+'\n')
p=ROOT/'Lab3.qsf';t=p.read_text()
for name in ['state4bit','state4bit_register']:
 t=t.replace(f'set_global_assignment -name VERILOG_FILE Tools/{name}.v',f'set_global_assignment -name BDF_FILE Tools/{name}.bdf')
p.write_text(t)
print('Created two BDF schematics and switched the project source assignments.')
