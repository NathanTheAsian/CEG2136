from pathlib import Path
import ast,subprocess,re,itertools,json,csv,bisect,shutil
from inspect_bdf import parse,fs,f
BASE=Path(__file__).resolve().parent;LAB=BASE.parent.parent;BIN=Path(r'C:\altera\13.0sp1\quartus\bin64')
a=ast.parse((BASE/'run_checks.py').read_text());exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
folder=BASE/'Lab3_top';folder.mkdir(exist_ok=True)
sources=[LAB/x for x in re.findall(r'set_global_assignment -name BDF_FILE ([^\r\n]+)',(LAB/'Lab3.qsf').read_text())]
for p in sources:shutil.copy2(p,folder/p.name)
common='set_global_assignment -name FAMILY "Cyclone III"\nset_global_assignment -name DEVICE AUTO\nset_global_assignment -name TOP_LEVEL_ENTITY Lab3_top\nset_global_assignment -name SIMULATION_MODE FUNCTIONAL\n'
common+=''.join('set_global_assignment -name BDF_FILE '+p.name+'\n' for p in sources)
(folder/'Check.qpf').write_text('PROJECT_REVISION = "Check"\n');(folder/'Check.qsf').write_text(common)
code,msg=run(folder,'quartus_map',['--generate_functional_sim_netlist','Check'],'netlist.log');print('NETLIST',code,msg,flush=True);assert code==0,msg
ps=ports(folder/'Lab3_top.bdf');clock=[n for n,d in ps if d=='INPUT' and n not in [p+str(i) for p in ['A','B','S'] for i in range(4)]];assert len(clock)==1;clock=clock[0]
waveout=LAB/'Waveforms'/'Verified';waveout.mkdir(exist_ok=True)
# Run the user's existing waveform unchanged.
shutil.copy2(LAB/'Tools/toptest.vwf',folder/'existing_input.vwf')
code,msg=run(folder,'quartus_sim',['Check','--mode=functional','--vector_source=existing_input.vwf','--write_settings_files=off','--simulation_results_format=VWF'],'existing.log')
if code==0:shutil.copy2(folder/'db/Check.sim.vwf',waveout/'Lab3_top_existingtest.vwf')
print('EXISTING WAVEFORM',code,msg,flush=True)
summary=[]
for s in range(16):
 cases=[];expected_cases=[]
 for b,a in itertools.product(range(16),repeat=2):
  if s<8:
   exact=[signed(a)+signed(b),signed(a)+signed(b)+1,signed(a),signed(a)+1,signed(a)-signed(b)-1,signed(a)-signed(b),~signed(a),-signed(a)][s]
   r=exact&15;v=int(not -8<=exact<=7)
   op0=a if s<6 else a^15;op1=b if s<2 else (b^15 if s in [4,5] else 0)
   cy=int(op0+op1+(s&1)>15)
  else:
   r=[0,15,a&b,a|b,a^b,a&(~b&15),(a<<1)&15,(a>>1)|(a&8)][s-8];v=0;cy=0
  exp=dict(**bits('C',r),V=v,Z=int(r==0),N=(r>>3)&1,Cy=cy)
  inputs=dict(**bits('A',a),**bits('B',b),**bits('S',s))
  expected_cases.append((inputs,exp))
  for clk in [0,1,0,1]:cases.append((dict(inputs,**{clock:clk}),{}))
 label=f'Lab3_top_S{s:04b}test';waveform(folder/(label+'.vwf'),ps,cases)
 args=['Check','--mode=functional','--vector_source='+label+'.vwf','--write_settings_files=off']
 code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VCD'],label+'.log');assert code==0,msg
 times,states=vcd_states(folder/'db/Check.sim.vcd');rows=[];failures=0;result_bad=0;flag_bad={k:0 for k in ['V','Z','N','Cy']};examples=[]
 for i,(inputs,expected) in enumerate(expected_cases):
  t=i*100000+87500;actual=states[bisect.bisect_right(times,t)-1]
  assert all(actual[k]==str(x) for k,x in inputs.items())
  wrong={k:dict(expected=x,actual=actual.get(k)) for k,x in expected.items() if actual.get(k)!=str(x)}
  failures+=bool(wrong);result_bad+=any(k in wrong for k in ['C0','C1','C2','C3'])
  for k in flag_bad:flag_bad[k]+=k in wrong
  observed={k:actual.get(k) for k in expected}
  rows.append(dict(time_ns=t/1000,inputs=inputs,expected=expected,actual=observed,wrong=wrong))
  if wrong and len(examples)<3:examples.append(rows[-1])
 (folder/(label+'.json')).write_text(json.dumps(rows,indent=2))
 code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VWF'],label+'_vwf.log');assert code==0,msg
 shutil.copy2(folder/'db/Check.sim.vwf',waveout/(label+'.vwf'))
 row=dict(S=f'{s:04b}',cases=256,passed=256-failures,result_failures=result_bad,flag_failures=flag_bad,examples=examples)
 summary.append(row);print({k:v for k,v in row.items() if k!='examples'},flush=True)
 (folder/'results.json').write_text(json.dumps(summary,indent=2))
changed=[str(p) for p in sources if p.read_bytes()!=(folder/p.name).read_bytes()]
print('CHANGED DURING TEST',changed,flush=True)
lines=['# Lab3_top functional test','','All 4096 A/B/selector combinations tested. Clock: '+clock+'. Each vector is held for two rising edges to accommodate the input and output registers.','', 'Reference: Lab3 PDF Tables 1 and 2. V is zero for logic/shift operations (optional shift overflow omitted). Carry is the carry out of op0 + op1 + S0 for arithmetic, zero for logic.','','| S | Passing / 256 | Result failures | V failures | Z failures | N failures | Cy failures |','|---|---:|---:|---:|---:|---:|---:|']
for x in summary:lines.append(f"| {x['S']} | {x['passed']} | {x['result_failures']} | {x['flag_failures']['V']} | {x['flag_failures']['Z']} | {x['flag_failures']['N']} | {x['flag_failures']['Cy']} |")
lines+=['',f"Overall: {sum(x['passed'] for x in summary)}/4096 complete cases pass.",'','Waveforms: Lab3_top_S0000test.vwf through Lab3_top_S1111test.vwf. The existing user waveform was also run and saved as Lab3_top_existingtest.vwf.','', 'Detailed vectors, expected outputs, actual outputs and compiler/simulation logs: simulation/all_checks/Lab3_top/.','', 'Source files changed during test: '+str(changed)]
(waveout/'Lab3_top_Report.md').write_text('\n'.join(lines));print('DONE',flush=True)
