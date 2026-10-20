from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parent;lab=base.parent.parent;out=lab/'Waveforms'/'Verified'
r=json.loads((base/'results.json').read_text());r.sort(key=lambda x:x['circuit'])
manifest={}
for p in (base/'sources').glob('*.bdf'):
 original=next(lab.glob('*/'+p.name))
 assert original.read_bytes()==p.read_bytes(),f'Changed during testing: {original}'
 manifest[str(original)]=hashlib.sha256(p.read_bytes()).hexdigest()
lines=['# Lab3 compilation and functional verification','','Reference: CEG2136_Lab3.pdf, Tables 1-3.','','All nine saved source circuits were recompiled in isolated verification projects. See compilation status below. Compilation does not establish functional correctness.','','| Circuit | Passing cases | Total | Compilation |','|---|---:|---:|---|']
total=failed=0
for e in r:
 n=sum(t.get('cases',0) for t in e['tests']);bad=sum(t.get('failures',0) for t in e['tests']);total+=n;failed+=bad
 lines.append(f"| {e['circuit']} | {n-bad} | {n} | {'PASS' if e['compile_ok'] else 'FAIL'} |")
lines+=['',f'Total: {total-failed}/{total} cases pass. A case passes only when all checked outputs match.','','## Remaining faults','',
'1. **4bitArithmeticCircuit:** Cy_out is connected to the M input of FourBitAdder. M also complements B, so this is not an independent carry-in. The lab requires op0 + op1 + S0. Use a four-bit adder with independent carry-in (e.g. four FAddr stages), or compensate for the existing M-controlled B inversion. The final carry C4 is not exposed at the circuit output; it will be needed for the lab carry-status flag.',
'2. **1bitLogicCircuit:** AND2 inst16 has both inputs connected to NOT B. For selector 101 it must compute A AND NOT B; connect one input to A.',
'3. **4bitLogicCircuit:** S0 is unconnected on bit-1 instance inst3. Connect it to S0. The shift data sources are reversed relative to the PDF: code 110 must route bit i-1 to output bit i (bit 0 receives zero), and code 111 must route bit i+1 to output bit i (bit 3 repeats A3). The mask fault in 1bitLogicCircuit is inherited.','','## Test scope','',
'- Multiplexer E is active-high, matching these custom circuits and the earlier agreed truth table. Stock multiplexer examples in the PDF use active-low enable and are different components.',
'- The 1-bit arithmetic outputs are checked against op0/op1/Cy in Table 3. Its selector connections were updated during verification; the latest saved version passed the rerun.',
'- Four-bit arithmetic OV is checked against the exact signed result outside -8 to +7. Complement alone does not overflow.',
'- For 4-bit logic, ASL is held at 0 and ASR at A3 for the required arithmetic shifts. All 256 A/B pairs are checked for every selector. Arbitrary external fill-bit combinations are not tested.',
'- The 1-bit logic test varies both neighbor inputs independently; A_left supplies operation 110 and A_right supplies operation 111.',
'- Functional simulation uses Cyclone III, the native Quartus simulator workaround for Cyclone IV. Hardware compilation uses the existing target EP4CE30F29C7. The PDF specifies EP4CE115F29C7; configure that target before programming its DE2-115 board.',
'- The 4-bit register is tested with all 16 data values, rising-edge loading, data changes while the clock is held high/low, falling-edge hold, and asynchronous active-low clear at both clock levels. No status-register circuit or complete ALU top-level was present.',
'- Samples are checked 12.5 ns into each 25 ns vector. This checks combinational behavior, not physical timing closure.','','## Saved files','',
'- Lab3.qsf source paths were corrected for Arithmetic, Logic, and Tools. Original settings are backed up in simulation/all_checks/Lab3.original.qsf. No BDF circuits were edited by this verification task.',
'- Waveforms here contain actual simulation results and end in test.vwf (the Quartus extension). Each holds at most 256 vectors.',
'- Input VWFs, CSV comparisons, VCDs, compiler logs, run_checks.py and results.json are under simulation/all_checks/.','','## Waveforms','','| Waveform | Passing / tested |','|---|---|']
for e in r:
 for t in e['tests']:
  n=t.get('cases',0);bad=t.get('failures',0);name=Path(t['waveform']).name
  lines.append(f'| [{name}]({name}) | {n-bad}/{n} |')
lines+=['','## First failing vector per test','']
for e in r:
 for t in e['tests']:
  if not t.get('examples'):continue
  ex=t['examples'][0];lines.append(f"- {t['name']}, {ex['time_ns']} ns: inputs `{json.dumps(ex['inputs'])}`; mismatches `{json.dumps(ex['wrong'])}`.")
(base/'tested_sources.json').write_text(json.dumps(manifest,indent=2))
(out/'VerificationReport.md').write_text('\n'.join(lines),encoding='utf-8')
print('\n'.join(lines[:19]));print('Waveforms:',len(list(out.glob('*test.vwf'))));print('Current sources match tested snapshots.')
