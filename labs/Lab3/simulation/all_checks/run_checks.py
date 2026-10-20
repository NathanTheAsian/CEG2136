from pathlib import Path
import subprocess,re,itertools,json,csv,bisect,shutil
from inspect_bdf import parse,fs,f
BASE=Path(__file__).resolve().parent
LAB=BASE.parent.parent
BIN=Path(r'C:\altera\13.0sp1\quartus\bin64')
WAV=LAB/'Waveforms'/'Verified'; WAV.mkdir(exist_ok=True)
SRC=BASE/'sources';SRC.mkdir(exist_ok=True)
sources=sorted(p for folder in ['Arithmetic','Logic','Tools'] for p in (LAB/folder).glob('*.bdf'))
for p in sources:shutil.copy2(p,SRC/p.name)
def ports(p):
 return [(fs(b,'text')[1][1], 'INPUT' if fs(b,'input') else 'OUTPUT') for b in parse(p.read_text()) if b[0]=='pin']
def bits(prefix,n,w=4):return {prefix+str(i):(n>>i)&1 for i in range(w)}
def signed(n):return n if n<8 else n-16
def testsets(name):
 if name=='FAddr':
  cases=[]
  for a,b,c in itertools.product(range(2),repeat=3):
   n=a+b+c;cases.append((dict(A=a,B=b,C_in=c),dict(Sum=n&1,C_out=n>>1)))
  return [('FAddr',cases)]
 if name in ['FourOneMUX','EightOneMUX']:
  width=2 if name=='FourOneMUX' else 3; count=2**width;sets=[]
  for e in range(2):
   for s in range(count):
    cases=[(dict(**bits('D',d,count),**bits('S',s,width),E=e),{('Out' if width==2 else 'CA'):e*((d>>s)&1)}) for d in range(2**count)]
    sets.append((f'{name}_S{s:0{width}b}_E{e}',cases))
  return sets
 if name=='FourBitAdder':
  sets=[]
  for m in range(2):
   cases=[]
   for b,a in itertools.product(range(16),repeat=2):
    exact=signed(a)+signed(b) if m==0 else signed(a)-signed(b)
    total=a+(b if m==0 else (b^15))+m
    cases.append((dict(**bits('A',a),**bits('B',b),M=m),dict(**bits('SA',exact&15),OV=int(not -8<=exact<=7),C4=(total>>4)&1)))
   sets.append((name+('ADD' if m==0 else 'SUB'),cases))
  return sets
 if name=='1bitArithmeticCircuit':
  cases=[]
  for s in range(8):
   for a,b in itertools.product(range(2),repeat=2):
    op0=a if s<6 else 1-a;op1=b if s<2 else (1-b if s in (4,5) else 0)
    cases.append((dict(**bits('S',s,3),A=a,B=b),dict(A_out=op0,B_out=op1,Cy_out=s&1)))
  return [(name,cases)]
 if name=='4bitArithmeticCircuit':
  sets=[]
  for s in range(8):
   cases=[]
   for b,a in itertools.product(range(16),repeat=2):
    sa,sb=signed(a),signed(b)
    exact=[sa+sb,sa+sb+1,sa,sa+1,sa-sb-1,sa-sb,~sa,-sa][s]
    cases.append((dict(**bits('A',a),**bits('B',b),**bits('S',s,3)),dict(**bits('CA',exact&15),OV=int(not -8<=exact<=7))))
   sets.append((f'{name}_S{s:03b}',cases))
  return sets
 if name=='1bitLogicCircuit':
  cases=[]
  for s in range(8):
   for a,b,left,right in itertools.product(range(2),repeat=4):
    r=[0,1,a&b,a|b,a^b,a&(1-b),left,right][s]
    cases.append((dict(**bits('S',s,3),A=a,B=b,A_left=left,A_right=right),dict(A_out=r)))
  return [(name,cases)]
 if name=='4bitLogicCircuit':
  sets=[]
  for s in range(8):
   cases=[]
   for b,a in itertools.product(range(16),repeat=2):
    value=[0,15,a&b,a|b,a^b,a&(~b&15),(a<<1)&15,((a>>1)|(a&8))][s]
    cases.append((dict(**bits('A',a),**bits('B',b),**bits('S',s,3),ASL=0,ASR=(a>>3)),bits('CI',value)))
   sets.append((f'{name}_S{s:03b}',cases))
  return sets
 if name=='4bitRegister':
  cases=[];q=0;previous_clock=0
  def step(data,clock,clear):
   nonlocal q,previous_clock
   if clear==0:q=0
   elif previous_clock==0 and clock==1:q=data
   cases.append((dict(**bits('P',data),CLK=clock,CLRN=clear),bits('Q',q)))
   previous_clock=clock
  step(15,0,0)
  for data in range(16):
   step(data,0,1)
   step(data,1,1)
   step(data^15,1,1)
   step(data^15,0,1)
   step(data,0,1)
  for clock in [0,1]:
   step(15,0,1);step(15,1,1)
   step(15,clock,1)
   step(15,clock,0)
   step(5,1-clock,0)
   step(10,clock,0)
   step(10,clock,1)
   step(10,0,1);step(10,1,1)
  return [(name,cases)]
 raise ValueError(name)
def waveform(path,ports,cases):
 duration=25*len(cases)
 t=f'HEADER\n{{\n VERSION = 1;\n TIME_UNIT = ns;\n DATA_OFFSET = 0.0;\n DATA_DURATION = {duration}.0;\n SIMULATION_TIME = 0.0;\n GRID_PHASE = 0.0;\n GRID_PERIOD = 25.0;\n GRID_DUTY_CYCLE = 50;\n}}\n'
 for name,direction in ports:
  t+=f'SIGNAL("{name}")\n{{\n VALUE_TYPE = NINE_LEVEL_BIT;\n SIGNAL_TYPE = SINGLE_BIT;\n WIDTH = 1;\n LSB_INDEX = -1;\n DIRECTION = {direction};\n PARENT = "";\n}}\n'
 for name,direction in ports:
  t+=f'TRANSITION_LIST("{name}")\n{{\n NODE\n {{\n REPEAT = 1;\n'
  for inputs,_ in cases:t+=f' LEVEL {inputs[name] if direction=="INPUT" else "X"} FOR 25.0;\n'
  t+=' }\n}\n'
 path.write_text(t)
def run(folder,exe,args,log):
 proc=subprocess.run([str(BIN/(exe+'.exe'))]+args,cwd=folder,capture_output=True,text=True)
 (folder/log).write_text(proc.stdout+proc.stderr)
 return proc.returncode, [line for line in (proc.stdout+proc.stderr).splitlines() if line.startswith('Error') or line.startswith('Warning')]
def vcd_states(path):
 text=path.read_text(); names={k:v for k,v in re.findall(r'\$var \w+ 1 (\S+) (\S+) \$end',text)};times=[];states=[];state={}
 assert re.search(r'\$timescale\s+1 ps',text)
 for b in re.split(r'(?m)^#',text)[1:]:
  ls=b.splitlines();time=int(ls[0])
  for line in ls[1:]:
   if line and line[0] in '01xXzZ' and line[1:] in names:state[names[line[1:]]]=line[0]
  times.append(time);states.append(state.copy())
 return times,states
results=json.loads((BASE/"results.json").read_text()) if (BASE/"results.json").exists() else []
for p in sources:
 name=p.stem
 if any(r['circuit']==name for r in results):continue
 folder=BASE/name;folder.mkdir(exist_ok=True);print('START',name,flush=True)
 ps=ports(p); sets=testsets(name)
 for label,cases in sets:waveform(folder/(label+'test.vwf'),ps,cases)
 (folder/'Check.qpf').write_text('PROJECT_REVISION = "Check"\n')
 common=f'set_global_assignment -name TOP_LEVEL_ENTITY {name}\nset_global_assignment -name PROJECT_OUTPUT_DIRECTORY output_files\n'
 for sp in sources:common+=f'set_global_assignment -name BDF_FILE "{(SRC/sp.name).as_posix()}"\n'
 (folder/'Check.qsf').write_text('set_global_assignment -name FAMILY "Cyclone IV E"\nset_global_assignment -name DEVICE EP4CE30F29C7\n'+common)
 code,errors=run(folder,'quartus_sh',['--flow','compile','Check'],'compile.log')
 entry=dict(circuit=name,compile_ok=code==0,compile_messages=errors,tests=[]);results.append(entry)
 print('COMPILE',name,'PASS' if code==0 else errors,flush=True)
 (folder/'Check.qsf').write_text('set_global_assignment -name FAMILY "Cyclone III"\nset_global_assignment -name DEVICE AUTO\nset_global_assignment -name SIMULATION_MODE FUNCTIONAL\n'+common)
 code,errors=run(folder,'quartus_map',['--generate_functional_sim_netlist','Check'],'netlist.log')
 entry['netlist_ok']=code==0;entry['netlist_messages']=errors
 if code:
  print('NETLIST FAILED',name,errors,flush=True);continue
 for label,cases in sets:
  inp=label+'test.vwf'; args=['Check','--mode=functional','--vector_source='+inp,'--write_settings_files=off']
  code,errors=run(folder,'quartus_sim',args+['--simulation_results_format=VCD'],label+'.log')
  if code:entry['tests'].append(dict(name=label,errors=errors));continue
  vcd=folder/'db'/'Check.sim.vcd';shutil.copy2(vcd,folder/(label+'.vcd'));times,states=vcd_states(vcd)
  rows=[];bad=[];bad_out={}
  for i,(inputs,expected) in enumerate(cases):
   time=i*25000+12500;actual=states[bisect.bisect_right(times,time)-1]
   assert all(actual[k]==str(v) for k,v in inputs.items()),(name,i,inputs,actual)
   wrong={k:dict(actual=actual.get(k),expected=v) for k,v in expected.items() if actual.get(k)!=str(v)}
   for k in wrong:bad_out[k]=bad_out.get(k,0)+1
   if wrong:bad.append(dict(time_ns=time/1000,inputs=inputs,wrong=wrong))
   rows.append(dict(time_ns=time/1000,inputs=json.dumps(inputs),expected=json.dumps(expected),actual=json.dumps({k:actual.get(k) for k in expected}),passed=not wrong))
  with (folder/(label+'.csv')).open('w',newline='') as out:
   w=csv.DictWriter(out,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
  code,errors=run(folder,'quartus_sim',args+['--simulation_results_format=VWF'],label+'_vwf.log')
  output=None
  if code==0:
   output=WAV/(label+'test.vwf');shutil.copy2(folder/'db'/'Check.sim.vwf',output)
  entry['tests'].append(dict(name=label,cases=len(cases),failures=len(bad),failed_outputs=bad_out,examples=bad[:5],waveform=str(output)))
  print('TEST',label,len(cases),'cases',len(bad),'failures',bad_out,flush=True)
 (BASE/'results.json').write_text(json.dumps(results,indent=2))
(BASE/'results.json').write_text(json.dumps(results,indent=2))
print('FINISHED',flush=True)
