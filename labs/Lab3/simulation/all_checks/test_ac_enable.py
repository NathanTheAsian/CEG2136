from pathlib import Path
import ast,subprocess,re,itertools,json,csv,bisect,shutil
from inspect_bdf import parse,fs,f
BASE=Path(__file__).resolve().parent;LAB=BASE.parent.parent;BIN=Path(r'C:\altera\13.0sp1\quartus\bin64')
module=ast.parse((BASE/'run_checks.py').read_text())
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
folder=BASE/'AC_enable';folder.mkdir(exist_ok=True)
sources=[LAB/'Arithmetic'/n for n in ['4bitArithmeticCircuit.bdf','1bitArithmeticCircuit.bdf','FourBitAdder.bdf','FAddr.bdf']]+[LAB/'Tools'/'FourOneMUX.bdf']
for p in sources:shutil.copy2(p,folder/p.name)
(folder/'Check.qpf').write_text('PROJECT_REVISION = "Check"\n')
q='set_global_assignment -name FAMILY "Cyclone III"\nset_global_assignment -name DEVICE AUTO\nset_global_assignment -name TOP_LEVEL_ENTITY 4bitArithmeticCircuit\nset_global_assignment -name SIMULATION_MODE FUNCTIONAL\n'
q+=''.join('set_global_assignment -name BDF_FILE '+p.name+'\n' for p in sources)
(folder/'Check.qsf').write_text(q)
code,msg=run(folder,'quartus_map',['--generate_functional_sim_netlist','Check'],'netlist.log');print('NETLIST',code,msg,flush=True)
assert code==0
ps=ports(folder/'4bitArithmeticCircuit.bdf');summary=[];rows=[]
for e in range(2):
 for s in range(8):
  label=f'4bitArithmeticCircuit_E{e}_S{s:03b}test';cases=[]
  for b,a in itertools.product(range(16),repeat=2):
   op0=a if s<6 else a^15;op1=b if s<2 else (b^15 if s in (4,5) else 0);m=s&1
   raw=op0+(op1 if m==0 else op1^15)+m
   cases.append((dict(**bits('A',a),**bits('B',b),**bits('S',s,3),E=e),bits('CA',(raw&15) if e else 0)))
  waveform(folder/(label+'.vwf'),ps,cases)
  args=['Check','--mode=functional','--vector_source='+label+'.vwf','--write_settings_files=off']
  code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VCD'],label+'.log');assert code==0,msg
  times,states=vcd_states(folder/'db'/'Check.sim.vcd');fails=0;ov_high=0;carry_high=0;examples=[]
  for i,(inputs,expected) in enumerate(cases):
   t=i*25000+12500;actual=states[bisect.bisect_right(times,t)-1]
   assert all(actual[k]==str(v) for k,v in inputs.items())
   ok=all(actual.get(k)==str(v) for k,v in expected.items());fails+=not ok
   ov_high+=actual['OV']=='1';carry_high+=actual['C_out']=='1'
   if e==0 and (actual['OV']=='1' or actual['C_out']=='1') and len(examples)<2:examples.append(dict(inputs=inputs,OV=actual['OV'],C_out=actual['C_out']))
   rows.append(dict(inputs=inputs,actual={k:actual[k] for k,d in ps if d=='OUTPUT'},data_enable_pass=ok))
  code,msg=run(folder,'quartus_sim',args+['--simulation_results_format=VWF'],label+'_vwf.log');assert code==0,msg
  dest=LAB/'Waveforms'/'Verified'/(label+'.vwf');shutil.copy2(folder/'db'/'Check.sim.vwf',dest)
  summary.append(dict(E=e,S=s,cases=256,data_failures=fails,OV_high=ov_high,C_out_high=carry_high,examples=examples))
  print(label,'data failures',fails,'OV high',ov_high,'C_out high',carry_high,flush=True)
for p in sources:assert p.read_bytes()==(folder/p.name).read_bytes(),f'Changed during run: {p}'
(folder/'results.json').write_text(json.dumps(summary,indent=2));(folder/'vectors.json').write_text(json.dumps(rows,indent=2))
text=['# 4-bit arithmetic enable test','','Tested 4096 combinations: 256 A/B pairs, 8 operations, both E levels.','', 'Data enable checks compare E=0 with zero, and E=1 with the existing internal operand-selection and ADD/SUB behavior. They do not certify the internal arithmetic against the lab table.','',f'Data enable failures: {sum(x["data_failures"] for x in summary)}.',f'Disabled OV high cases: {sum(x["OV_high"] for x in summary if x["E"]==0)}.',f'Disabled C_out high cases: {sum(x["C_out_high"] for x in summary if x["E"]==0)}.','','OV and C_out are directly connected to the adder and are not gated by E.','', 'Waveforms are named 4bitArithmeticCircuit_E0_S000test.vwf etc., in this folder.']
(LAB/'Waveforms'/'Verified'/'AC_Enable_Report.md').write_text('\n'.join(text))
print('DONE',flush=True)
