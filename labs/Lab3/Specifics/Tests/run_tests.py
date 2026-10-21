"""Build current Lab3 BDF sources, then run all four exhaustive top-level tests."""
from pathlib import Path
import os
import re
import subprocess
import sys

lab = Path(__file__).resolve().parents[1]
base = lab / "simulation" / "test_run"
base.mkdir(parents=True, exist_ok=True)
quartus_bin = Path(os.environ.get('QUARTUS_BIN', 'C:/altera/13.0sp1/quartus/bin64'))
mapper = quartus_bin / ('quartus_map.exe' if os.name == 'nt' else 'quartus_map')
settings = [
    'set_global_assignment -name FAMILY "Cyclone III"',
    'set_global_assignment -name DEVICE AUTO',
    'set_global_assignment -name TOP_LEVEL_ENTITY Lab3_top',
    'set_global_assignment -name SIMULATION_MODE FUNCTIONAL',
]
# Isolated legacy functional-simulator project; leave the board project untouched.
for source in re.findall(r'^set_global_assignment -name BDF_FILE (.+)$',
                         (lab / 'Lab3.qsf').read_text(), re.M):
    path = (lab / source.strip().strip('"')).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    settings.append(f'set_global_assignment -name BDF_FILE "{path.as_posix()}"')
(base / 'Check.qsf').write_text('\n'.join(settings) + '\n')
(base / 'Check.qpf').write_text('PROJECT_REVISION = "Check"\n')
print('Building current Lab3 functional netlist...', flush=True)
result = subprocess.run([str(mapper), '--generate_functional_sim_netlist', 'Check'],
                        cwd=base, capture_output=True, text=True)
(base / 'rebuild.log').write_text(result.stdout + result.stderr)
if result.returncode:
    print(result.stdout + result.stderr)
    sys.exit(2)
print('Running 4 waveforms / 4096 input combinations...', flush=True)
result = subprocess.run([sys.executable, str(Path(__file__).with_name('diagnose.py'))], cwd=lab)
sys.exit(result.returncode)
