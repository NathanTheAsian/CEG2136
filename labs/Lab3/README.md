# Lab 3

Open Lab3.qpf in Quartus. Settings: Lab3.qsf.

- Arithmetic/, Logic/, Tools/: active BDF sources and symbols.
- Tests/: exhaustive test runner and checker.
- Reports/: current summary and detailed results.
- Waveforms/Exhaustive/: four exhaustive input waveforms.
- Waveforms/Results/: simulated output waveforms.
- Waveforms/ComponentTests/: original component stimuli.
- Waveforms/Original/: original top-level stimulus.
- simulation/test_run/: generated simulation project, logs and databases.
- db/, incremental_db/, output_files/: generated Quartus files.
- Archive/previous_verification.zip: historical scripts, simulations, reports and pre-fix source backups. Old failures refer to earlier circuit versions.

Run in Git Bash from this folder: bash run_tests.sh
From repository root: bash labs/Lab3/run_tests.sh
Returns zero only if all 4096 cases pass. Override executable locations with PYTHON and QUARTUS_BIN.
