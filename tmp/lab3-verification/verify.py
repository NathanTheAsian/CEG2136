"""Verify active Lab3 sources in an isolated Quartus functional simulation."""
from pathlib import Path
import bisect
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'labs/Lab3'
BASE = Path(__file__).resolve().parent
BUILD = BASE / 'simulation'
BUILD.mkdir(exist_ok=True)
BIN = Path('C:/altera/13.0sp1/quartus/bin64')
qsf = (LAB / 'Lab3.qsf').read_text()
settings = [
    'set_global_assignment -name FAMILY "Cyclone III"',
    'set_global_assignment -name DEVICE AUTO',
    'set_global_assignment -name TOP_LEVEL_ENTITY Lab3_top',
    'set_global_assignment -name SIMULATION_MODE FUNCTIONAL',
]
manifest = {}
for source in re.findall(r'^set_global_assignment -name BDF_FILE (.+)$', qsf, re.M):
    source = source.strip().strip('"')
    original = LAB / source
    copy = BASE / 'sources' / source
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, copy)
    manifest[source] = hashlib.sha256(original.read_bytes()).hexdigest()
    settings.append(f'set_global_assignment -name BDF_FILE "{copy.as_posix()}"')
(BASE / 'source_hashes.json').write_text(json.dumps(manifest, indent=2))
(BUILD / 'Check.qsf').write_text('\n'.join(settings) + '\n')
(BUILD / 'Check.qpf').write_text('PROJECT_REVISION = "Check"\n')

def run(executable, args, log):
    result = subprocess.run([str(BIN / executable), *args], cwd=BUILD,
                            capture_output=True, text=True)
    (BASE / log).write_text(result.stdout + result.stderr)
    if result.returncode:
        print(result.stdout + result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout + result.stderr

print('Building a snapshot of the active Lab3.qsf sources...', flush=True)
run('quartus_map.exe', ['--generate_functional_sim_netlist', 'Check'], 'build.log')

OPERATIONS = [
    'A + B', 'A + B + 1', 'A', 'A + 1', 'A - B - 1', 'A - B',
    '~A', '-A', '0', '15', 'A & B', 'A | B', 'A ^ B', 'A & ~B',
    'arithmetic shift left A', 'arithmetic shift right A',
]

def expected(a, b, s):
    return [a+b, a+b+1, a, a+1, a-b-1, a-b, ~a, -a,
            0, 15, a&b, a|b, a^b, a&~b, a<<1,
            (a>>1)|(a&8)][s] & 15

def read_vcd(path):
    text = path.read_text()
    names = dict(re.findall(r'\$var \w+ 1 (\S+) (\S+) \$end', text))
    scale = re.search(r'\$timescale\s+(\d+)\s*(\w+)\s+\$end', text)
    factors = {'s': 1e9, 'ms': 1e6, 'us': 1e3, 'ns': 1, 'ps': 1e-3, 'fs': 1e-6}
    tick_ns = int(scale[1]) * factors[scale[2]]
    ts, states, state = [], [], {}
    for block in re.split(r'(?m)^#', text)[1:]:
        lines = block.splitlines()
        for line in lines[1:]:
            if line and line[0] in '01xXzZ' and line[1:] in names:
                state[names[line[1:]]] = line[0].lower()
        ts.append(int(lines[0]) * tick_ns)
        states.append(state.copy())
    def at(ns):
        index = bisect.bisect_right(ts, ns) - 1
        assert index >= 0, ns
        return states[index]
    return names, ts, states, at

def value(state, prefix):
    bits = [state.get(prefix + str(i), 'x') for i in range(4)]
    return sum(int(bit) << i for i, bit in enumerate(bits)) if all(b in '01' for b in bits) else ''.join(reversed(bits))

rows, reset, edge_errors = [], [], []
present_flags = None
for wave in sorted((LAB / 'Specifics/Waveforms/Exhaustive').glob('TopTest_A*_S*.vwf')):
    print('Simulating ' + wave.name, flush=True)
    run('quartus_sim.exe', ['Check', '--mode=functional', '--vector_source=' + str(wave),
        '--write_settings_files=off', '--simulation_results_format=VCD'], wave.stem + '.log')
    result_path = BASE / (wave.stem + '.vcd')
    shutil.copy2(BUILD / 'db/Check.sim.vcd', result_path)
    names, ts, states, at = read_vcd(result_path)
    flags = {f for f in ('Cy', 'V', 'Z', 'N') if f in names.values()}
    present_flags = sorted(flags)
    reset.append({'wave': wave.name, 'C_at_1ns': value(at(1), 'C'),
                  'C_at_19ns': value(at(19), 'C')})
    for i in range(1024):
        start = 20 + i * 40
        inputs = at(start + 1)
        a, b, s = [value(inputs, p) for p in ('A', 'B', 'S')]
        assert all(isinstance(x, int) for x in (a, b, s))
        want = expected(a, b, s)
        actual = value(at(start + 36), 'C')
        rows.append({'wave': wave.name, 'sample_ns': start+36, 'A': a, 'B': b,
                     'S': f'{s:04b}', 'expected_C': want, 'actual_C': actual,
                     'pass': want == actual})
        # Inputs are latched on the first rising edge, output on the second.
        at_second_edge = value(at(start + 16), 'C')
        if at_second_edge != actual:
            edge_errors.append({'wave': wave.name, 'start_ns': start,
                                'C_after_second_edge': at_second_edge, 'C_settled': actual})

assert len(rows) == 4096 and len({(r['A'], r['B'], r['S']) for r in rows}) == 4096
summary = []
for s in range(16):
    cases = [r for r in rows if r['S'] == f'{s:04b}']
    entry = {'S': f'{s:04b}', 'operation': OPERATIONS[s], 'passed': sum(r['pass'] for r in cases),
             'total': len(cases), 'first_failure': next((r for r in cases if not r['pass']), None)}
    summary.append(entry)
    print(f"{entry['S']} {entry['operation']}: {entry['passed']}/{entry['total']}", flush=True)

assert all(hashlib.sha256((LAB / name).read_bytes()).hexdigest() == digest for name, digest in manifest.items()), 'Active sources changed during verification'
report = {'tested_project': str(LAB / 'Lab3.qsf'), 'total': 4096,
          'passed': sum(r['pass'] for r in rows), 'present_flags': present_flags,
          'missing_flags': sorted(set(('Cy', 'V', 'Z', 'N')) - set(present_flags)),
          'reset': reset, 'pipeline_settling_errors': edge_errors,
          'summary': summary, 'cases': rows}
(BASE / 'results.json').write_text(json.dumps(report, indent=2))
lines = ['# Active Lab 3 functional verification', '',
         'Compiled the BDF sources listed by labs/Lab3/Lab3.qsf, captured in source_hashes.json.',
         'Functional simulation uses an isolated Cyclone III project for the legacy Quartus simulator; no board timing or hardware is validated.',
         'All 4096 A/B/S combinations are covered. C is sampled after the input/output register pipeline settles.', '',
         f"Result: {report['passed']}/4096 result-word cases passed.",
         'Missing status outputs: ' + ', '.join(report['missing_flags']) + '.', '',
         '| S | Operation | Correct C / 256 |', '|---|---|---:|']
for entry in summary:
    lines.append(f"| {entry['S']} | {entry['operation'].replace('|', '&#124;')} | {entry['passed']} |")
lines += ['', '## First failure for each operation', '']
for entry in summary:
    row = entry['first_failure']
    if row:
        lines.append(f"- S={row['S']}, A={row['A']}, B={row['B']}: expected C={row['expected_C']}, actual C={row['actual_C']}.")
lines += ['', f"Reset checks: {json.dumps(reset)}", f"Output settling differences after the second rising edge: {len(edge_errors)}."]
(BASE / 'report.md').write_text('\n'.join(lines) + '\n')
print(f"Overall C: {report['passed']}/4096; missing flags: {report['missing_flags']}")
raise SystemExit(0 if report['passed'] == 4096 and not report['missing_flags'] else 1)
