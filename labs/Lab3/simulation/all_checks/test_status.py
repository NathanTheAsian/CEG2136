from pathlib import Path
import ast,subprocess,re,itertools,json,csv,bisect,shutil
from inspect_bdf import parse,fs,f
BASE=Path(__file__).resolve().parent;LAB=BASE.parent.parent;BIN=Path(r'C:\altera\13.0sp1\quartus\bin64')
a=ast.parse((BASE/'run_checks.py').read_text());exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
outputs=['V','Z','N','Cy'];inputs=['F3','F2','F1','F0','S3','CAR2','CAR3']
all_inputs=[dict(zip(inputs,vals)) for vals in itertools.product(range(2),repeat=7)]
def golden(v):
 value=sum(v['F'+str(i)]<<i for i in range(4))
 return dict(V=int(v['S3']==0 and v['CAR2']!=v['CAR3']),Z=int(value==0),N=int(value>=8),Cy=int(v['S3']==0 and v['CAR3']==1))
sets={'state4bit':[('state4bit',[(v,golden(v)) for v in all_inputs])], 'state4bit_register':[]}
for batch in range(4):
 cases=[];q=dict.fromkeys(outputs,0);prev=0
 def step(v,clk,clrn):
  global q,prev
  if not clrn:q=dict.fromkeys(outputs,0)
  elif not prev and clk:q=golden(v)
  cases.append((dict(v,CLK=clk,CLRN=clrn),q.copy()));prev=clk
 step(all_inputs[0],0,0)
 for v in all_inputs[batch*32:(batch+1)*32]:
  step(v,0,1);step(v,1,1)
  changed={k:1-x for k,x in v.items()}
  step(changed,1,1);step(changed,0,1)
 active=dict(F3=1,F2=0,F1=0,F0=0,S3=0,CAR2=0,CAR3=1)
 for clock in [1,0]:
  step(active,0,1);step(active,1,1);step(active,clock,1)
  step(active,clock,0);step(active,1-clock,0);step(active,clock,0)
  step(active,clock,1);step(active,0,1);step(active,1,1)
 sets['state4bit_register'].append((f'state4bit_register_{batch}',cases))
results=[]
for top,groups in sets.items():
 folder=BASE/top;folder.mkdir(exist_ok=True)
 common=f'set_global_assignment -name TOP_LEVEL_ENTITY {top}\n'
 for name in sets:
  src=LAB/'Tools'/(name+'.v');shutil.copy2(src,folder/src.name)
  common+=f'set_global_assignment -name VERILOG_FILE {src.name}\n'
 (folder/'Check.qpf').write_text('PROJECT_REVISION = "Check"\n')
 (folder/'Check.qsf').write_text('set_global_assignment -name FAMILY "Cyclone IV E"\nset_global_assignment -name DEVICE EP4CE30F29C7\n'+common)
 code,msg=run(folder,'quartus_sh',['--flow','compile','Check'],'compile.log');print('COMPILE',top,code,msg,flush=True);assert code==0
 (folder/'Check.qsf').write_text('set_global_assignment -name FAMILY "Cyclone III"\nset_global_assignment -name DEVICE AUTO\nset_global_assignment -name SIMULATION_MODE FUNCTIONAL\n'+common)
 code,msg=run(folder,'quartus_map',['--generate_functional_sim_netlist','Check'],'netlist.log');assert code==0,msg
 ps=[(k,'INPUT') for k in inputs+(['CLK','CLRN'] if top.endswith('register') else [])]+[(k,'OUTPUT') for k in outputs]
 for label,cases in groups:
  waveform(folder/(label+'test.vwf'),ps,cases)
  args=['Check','--mode=functional','--vector_source='+label+'test.vwf','--write_settings_files=off']
  code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VCD'],label+'.log');assert code==0,msg
  times,states=vcd_states(folder/'db'/'Check.sim.vcd');rows=[]
  for i,(v,expected) in enumerate(cases):
   t=i*25000+12500;actual=states[bisect.bisect_right(times,t)-1]
   assert all(actual[k]==str(x) for k,x in v.items())
   wrong={k:dict(expected=x,actual=actual.get(k)) for k,x in expected.items() if actual.get(k)!=str(x)}
   rows.append(dict(time_ns=t/1000,inputs=v,expected=expected,actual={k:actual.get(k) for k in outputs},wrong=wrong))
  failures=sum(bool(r['wrong']) for r in rows)
  (folder/(label+'.json')).write_text(json.dumps(rows,indent=2))
  code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VWF'],label+'_vwf.log');assert code==0,msg
  shutil.copy2(folder/'db'/'Check.sim.vwf',LAB/'Waveforms'/'Verified'/(label+'test.vwf'))
  results.append(dict(test=label,cases=len(cases),failures=failures));print(results[-1],flush=True)
  assert failures==0
(BASE/'status_results.json').write_text(json.dumps(results,indent=2));print('ALL STATUS TESTS PASS',flush=True)
