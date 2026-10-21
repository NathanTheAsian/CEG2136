from pathlib import Path
import re,subprocess,bisect,csv,json,os,shutil
lab=Path(__file__).resolve().parents[1]; base=lab/'simulation/test_run'; waves=lab/'Waveforms/Exhaustive'
reports=lab/'Reports'; reports.mkdir(exist_ok=True)
wave_results=lab/'Waveforms/Results'; wave_results.mkdir(exist_ok=True)
quartus_bin=Path(os.environ.get('QUARTUS_BIN',r'C:/altera/13.0sp1/quartus/bin64'))
simulator=quartus_bin/('quartus_sim.exe' if os.name=='nt' else 'quartus_sim')
summary=[];rows=[]
for wave in sorted(waves.glob('TopTest_A*_S*.vwf')):
 if '_result' in wave.stem:continue
 proc=subprocess.run([str(simulator),'Check','--mode=functional','--vector_source='+str(wave),'--write_settings_files=off','--simulation_results_format=VCD'],cwd=base,capture_output=True,text=True)
 assert proc.returncode==0,proc.stdout+proc.stderr
 (base/(wave.stem+'.log')).write_text(proc.stdout+proc.stderr)
 shutil.copy2(base/'db/Check.sim.vcd',base/(wave.stem+'.vcd'))
 text=(base/'db/Check.sim.vcd').read_text(); names=dict(re.findall(r'\$var \w+ 1 (\S+) (\S+) \$end',text));ts=[];states=[];state={}
 for block in re.split(r'(?m)^#',text)[1:]:
  ls=block.splitlines()
  for line in ls[1:]:
   if line and line[0] in '01xXzZ' and line[1:] in names:state[names[line[1:]]]=line[0]
  ts.append(int(ls[0]));states.append(state.copy())
 def at(ns):return states[bisect.bisect_right(ts,int(ns*1000))-1]
 def value(st,p):return sum(int(st[p+str(i)])<<i for i in range(4))
 for i in range(1024):
  t=20+i*40; inp=at(t+1);act=at(t+36);a,b,s=[value(inp,p) for p in ['A','B','S']];sa=a if a<8 else a-16;sb=b if b<8 else b-16
  if s<8:
   exact=[sa+sb,sa+sb+1,sa,sa+1,sa-sb-1,sa-sb,~sa,-sa][s];r=exact&15;v=int(not -8<=exact<=7)
   op0=a if s<6 else a^15;op1=b if s<2 else b^15 if s in [4,5] else 0;cy=int(op0+op1+(s&1)>15)
  else:r=[0,15,a&b,a|b,a^b,a&(~b&15),(a<<1)&15,(a>>1)|(a&8)][s-8];v=cy=0
  expected=dict(C=r,Cy=cy,V=v,Z=int(r==0),N=r>>3);actual=dict(C=value(act,'C'),**{k:int(act[k]) for k in ['Cy','V','Z','N']});wrong=[k for k in expected if expected[k]!=actual[k]]
  rows.append(dict(file=wave.name,time_ns=t+36,A=a,B=b,S=f'{s:04b}',expected=expected,actual=actual,wrong=wrong))
 proc=subprocess.run([str(simulator),'Check','--mode=functional','--vector_source='+str(wave),'--write_settings_files=off','--simulation_results_format=VWF'],cwd=base,capture_output=True,text=True)
 (base/(wave.stem+'_vwf.log')).write_text(proc.stdout+proc.stderr)
 assert proc.returncode==0,proc.stdout+proc.stderr
 shutil.copy2(base/'db/Check.sim.vwf',wave_results/(wave.stem+'_result.vwf'))
assert len(rows)==4096 and len({(r['A'],r['B'],r['S']) for r in rows})==4096, 'Incomplete or duplicate input coverage'
for s in range(16):
 selected=[r for r in rows if int(r['S'],2)==s];entry=dict(S=f'{s:04b}',passed=sum(not r['wrong'] for r in selected),failures={k:sum(k in r['wrong'] for r in selected) for k in ['C','Cy','V','Z','N']});summary.append(entry);print(entry)
(reports/'exhaustive_diagnosis.json').write_text(json.dumps(dict(summary=summary,cases=rows),indent=2))
lines=['# Current Lab3 circuit diagnosis','','All 4096 input combinations simulated against current BDF sources. Outputs sampled 36 ns after vector start, after input/output pipeline settling. V=0 for logic/shift operations (optional shift overflow omitted).','','| S | Pass / 256 | C failures | Cy failures | V failures | Z failures | N failures |','|---|---:|---:|---:|---:|---:|---:|']
for r in summary:lines.append('| '+r['S']+' | '+str(r['passed'])+' | '+' | '.join(str(r['failures'][k]) for k in ['C','Cy','V','Z','N'])+' |')
lines+=['',f"Total complete cases passing: {sum(r['passed'] for r in summary)}/4096.",'','Examples:']
for s in [0,1,9,13,14,15]:
 r=next((r for r in rows if int(r['S'],2)==s and r['wrong']),None)
 if r is None:continue
 lines.append(f"- S={r['S']}, A={r['A']}, B={r['B']}, time={r['time_ns']} ns: expected {r['expected']}; actual {r['actual']}.")
(reports/'Circuit_Diagnosis.md').write_text('\n'.join(lines))
passed=sum(r['passed'] for r in summary)
print(f'\n{passed}/4096 cases passed. Report: {reports / "Circuit_Diagnosis.md"}')
raise SystemExit(0 if passed==4096 else 1)

