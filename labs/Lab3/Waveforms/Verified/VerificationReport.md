# Lab3 compilation and functional verification

Reference: CEG2136_Lab3.pdf, Tables 1-3.

All nine saved source circuits were recompiled in isolated verification projects. See compilation status below. Compilation does not establish functional correctness.

| Circuit | Passing cases | Total | Compilation |
|---|---:|---:|---|
| 1bitArithmeticCircuit | 32 | 32 | PASS |
| 1bitLogicCircuit | 124 | 128 | PASS |
| 4bitArithmeticCircuit | 1024 | 2048 | PASS |
| 4bitLogicCircuit | 913 | 2048 | PASS |
| 4bitRegister | 99 | 99 | PASS |
| EightOneMUX | 4096 | 4096 | PASS |
| FAddr | 8 | 8 | PASS |
| FourBitAdder | 512 | 512 | PASS |
| FourOneMUX | 128 | 128 | PASS |

Total: 6936/9099 cases pass. A case passes only when all checked outputs match.

## Remaining faults

1. **4bitArithmeticCircuit:** Cy_out is connected to the M input of FourBitAdder. M also complements B, so this is not an independent carry-in. The lab requires op0 + op1 + S0. Use a four-bit adder with independent carry-in (e.g. four FAddr stages), or compensate for the existing M-controlled B inversion. The final carry C4 is not exposed at the circuit output; it will be needed for the lab carry-status flag.
2. **1bitLogicCircuit:** AND2 inst16 has both inputs connected to NOT B. For selector 101 it must compute A AND NOT B; connect one input to A.
3. **4bitLogicCircuit:** S0 is unconnected on bit-1 instance inst3. Connect it to S0. The shift data sources are reversed relative to the PDF: code 110 must route bit i-1 to output bit i (bit 0 receives zero), and code 111 must route bit i+1 to output bit i (bit 3 repeats A3). The mask fault in 1bitLogicCircuit is inherited.

## Test scope

- Multiplexer E is active-high, matching these custom circuits and the earlier agreed truth table. Stock multiplexer examples in the PDF use active-low enable and are different components.
- The 1-bit arithmetic outputs are checked against op0/op1/Cy in Table 3. Its selector connections were updated during verification; the latest saved version passed the rerun.
- Four-bit arithmetic OV is checked against the exact signed result outside -8 to +7. Complement alone does not overflow.
- For 4-bit logic, ASL is held at 0 and ASR at A3 for the required arithmetic shifts. All 256 A/B pairs are checked for every selector. Arbitrary external fill-bit combinations are not tested.
- The 1-bit logic test varies both neighbor inputs independently; A_left supplies operation 110 and A_right supplies operation 111.
- Functional simulation uses Cyclone III, the native Quartus simulator workaround for Cyclone IV. Hardware compilation uses the existing target EP4CE30F29C7. The PDF specifies EP4CE115F29C7; configure that target before programming its DE2-115 board.
- The 4-bit register is tested with all 16 data values, rising-edge loading, data changes while the clock is held high/low, falling-edge hold, and asynchronous active-low clear at both clock levels. No status-register circuit or complete ALU top-level was present.
- Samples are checked 12.5 ns into each 25 ns vector. This checks combinational behavior, not physical timing closure.

## Saved files

- Lab3.qsf source paths were corrected for Arithmetic, Logic, and Tools. Original settings are backed up in simulation/all_checks/Lab3.original.qsf. No BDF circuits were edited by this verification task.
- Waveforms here contain actual simulation results and end in test.vwf (the Quartus extension). Each holds at most 256 vectors.
- Input VWFs, CSV comparisons, VCDs, compiler logs, run_checks.py and results.json are under simulation/all_checks/.

## Waveforms

| Waveform | Passing / tested |
|---|---|
| [1bitArithmeticCircuittest.vwf](1bitArithmeticCircuittest.vwf) | 32/32 |
| [1bitLogicCircuittest.vwf](1bitLogicCircuittest.vwf) | 124/128 |
| [4bitArithmeticCircuit_S000test.vwf](4bitArithmeticCircuit_S000test.vwf) | 256/256 |
| [4bitArithmeticCircuit_S001test.vwf](4bitArithmeticCircuit_S001test.vwf) | 0/256 |
| [4bitArithmeticCircuit_S010test.vwf](4bitArithmeticCircuit_S010test.vwf) | 256/256 |
| [4bitArithmeticCircuit_S011test.vwf](4bitArithmeticCircuit_S011test.vwf) | 0/256 |
| [4bitArithmeticCircuit_S100test.vwf](4bitArithmeticCircuit_S100test.vwf) | 256/256 |
| [4bitArithmeticCircuit_S101test.vwf](4bitArithmeticCircuit_S101test.vwf) | 0/256 |
| [4bitArithmeticCircuit_S110test.vwf](4bitArithmeticCircuit_S110test.vwf) | 256/256 |
| [4bitArithmeticCircuit_S111test.vwf](4bitArithmeticCircuit_S111test.vwf) | 0/256 |
| [4bitLogicCircuit_S000test.vwf](4bitLogicCircuit_S000test.vwf) | 0/256 |
| [4bitLogicCircuit_S001test.vwf](4bitLogicCircuit_S001test.vwf) | 256/256 |
| [4bitLogicCircuit_S010test.vwf](4bitLogicCircuit_S010test.vwf) | 128/256 |
| [4bitLogicCircuit_S011test.vwf](4bitLogicCircuit_S011test.vwf) | 256/256 |
| [4bitLogicCircuit_S100test.vwf](4bitLogicCircuit_S100test.vwf) | 128/256 |
| [4bitLogicCircuit_S101test.vwf](4bitLogicCircuit_S101test.vwf) | 81/256 |
| [4bitLogicCircuit_S110test.vwf](4bitLogicCircuit_S110test.vwf) | 32/256 |
| [4bitLogicCircuit_S111test.vwf](4bitLogicCircuit_S111test.vwf) | 32/256 |
| [4bitRegistertest.vwf](4bitRegistertest.vwf) | 99/99 |
| [EightOneMUX_S000_E0test.vwf](EightOneMUX_S000_E0test.vwf) | 256/256 |
| [EightOneMUX_S001_E0test.vwf](EightOneMUX_S001_E0test.vwf) | 256/256 |
| [EightOneMUX_S010_E0test.vwf](EightOneMUX_S010_E0test.vwf) | 256/256 |
| [EightOneMUX_S011_E0test.vwf](EightOneMUX_S011_E0test.vwf) | 256/256 |
| [EightOneMUX_S100_E0test.vwf](EightOneMUX_S100_E0test.vwf) | 256/256 |
| [EightOneMUX_S101_E0test.vwf](EightOneMUX_S101_E0test.vwf) | 256/256 |
| [EightOneMUX_S110_E0test.vwf](EightOneMUX_S110_E0test.vwf) | 256/256 |
| [EightOneMUX_S111_E0test.vwf](EightOneMUX_S111_E0test.vwf) | 256/256 |
| [EightOneMUX_S000_E1test.vwf](EightOneMUX_S000_E1test.vwf) | 256/256 |
| [EightOneMUX_S001_E1test.vwf](EightOneMUX_S001_E1test.vwf) | 256/256 |
| [EightOneMUX_S010_E1test.vwf](EightOneMUX_S010_E1test.vwf) | 256/256 |
| [EightOneMUX_S011_E1test.vwf](EightOneMUX_S011_E1test.vwf) | 256/256 |
| [EightOneMUX_S100_E1test.vwf](EightOneMUX_S100_E1test.vwf) | 256/256 |
| [EightOneMUX_S101_E1test.vwf](EightOneMUX_S101_E1test.vwf) | 256/256 |
| [EightOneMUX_S110_E1test.vwf](EightOneMUX_S110_E1test.vwf) | 256/256 |
| [EightOneMUX_S111_E1test.vwf](EightOneMUX_S111_E1test.vwf) | 256/256 |
| [FAddrtest.vwf](FAddrtest.vwf) | 8/8 |
| [FourBitAdderADDtest.vwf](FourBitAdderADDtest.vwf) | 256/256 |
| [FourBitAdderSUBtest.vwf](FourBitAdderSUBtest.vwf) | 256/256 |
| [FourOneMUX_S00_E0test.vwf](FourOneMUX_S00_E0test.vwf) | 16/16 |
| [FourOneMUX_S01_E0test.vwf](FourOneMUX_S01_E0test.vwf) | 16/16 |
| [FourOneMUX_S10_E0test.vwf](FourOneMUX_S10_E0test.vwf) | 16/16 |
| [FourOneMUX_S11_E0test.vwf](FourOneMUX_S11_E0test.vwf) | 16/16 |
| [FourOneMUX_S00_E1test.vwf](FourOneMUX_S00_E1test.vwf) | 16/16 |
| [FourOneMUX_S01_E1test.vwf](FourOneMUX_S01_E1test.vwf) | 16/16 |
| [FourOneMUX_S10_E1test.vwf](FourOneMUX_S10_E1test.vwf) | 16/16 |
| [FourOneMUX_S11_E1test.vwf](FourOneMUX_S11_E1test.vwf) | 16/16 |

## First failing vector per test

- 1bitLogicCircuit, 2012.5 ns: inputs `{"S0": 1, "S1": 0, "S2": 1, "A": 0, "B": 0, "A_left": 0, "A_right": 0}`; mismatches `{"A_out": {"actual": "1", "expected": 0}}`.
- 4bitArithmeticCircuit_S001, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 0, "S2": 0}`; mismatches `{"CA0": {"actual": "0", "expected": 1}}`.
- 4bitArithmeticCircuit_S011, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 1, "S2": 0}`; mismatches `{"CA0": {"actual": "0", "expected": 1}}`.
- 4bitArithmeticCircuit_S101, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 0, "S2": 1}`; mismatches `{"CA0": {"actual": "1", "expected": 0}}`.
- 4bitArithmeticCircuit_S111, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 1, "S2": 1}`; mismatches `{"CA0": {"actual": "1", "expected": 0}, "CA1": {"actual": "1", "expected": 0}, "CA2": {"actual": "1", "expected": 0}, "CA3": {"actual": "1", "expected": 0}}`.
- 4bitLogicCircuit_S000, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 0, "S1": 0, "S2": 0, "ASL": 0, "ASR": 0}`; mismatches `{"CI1": {"actual": "1", "expected": 0}}`.
- 4bitLogicCircuit_S010, 62.5 ns: inputs `{"A0": 0, "A1": 1, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 0, "S1": 1, "S2": 0, "ASL": 0, "ASR": 0}`; mismatches `{"CI1": {"actual": "1", "expected": 0}}`.
- 4bitLogicCircuit_S100, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 0, "S1": 0, "S2": 1, "ASL": 0, "ASR": 0}`; mismatches `{"CI1": {"actual": "1", "expected": 0}}`.
- 4bitLogicCircuit_S101, 12.5 ns: inputs `{"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 0, "S2": 1, "ASL": 0, "ASR": 0}`; mismatches `{"CI0": {"actual": "1", "expected": 0}, "CI1": {"actual": "1", "expected": 0}, "CI2": {"actual": "1", "expected": 0}, "CI3": {"actual": "1", "expected": 0}}`.
- 4bitLogicCircuit_S110, 62.5 ns: inputs `{"A0": 0, "A1": 1, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 0, "S1": 1, "S2": 1, "ASL": 0, "ASR": 0}`; mismatches `{"CI0": {"actual": "1", "expected": 0}, "CI2": {"actual": "0", "expected": 1}}`.
- 4bitLogicCircuit_S111, 37.5 ns: inputs `{"A0": 1, "A1": 0, "A2": 0, "A3": 0, "B0": 0, "B1": 0, "B2": 0, "B3": 0, "S0": 1, "S1": 1, "S2": 1, "ASL": 0, "ASR": 0}`; mismatches `{"CI1": {"actual": "1", "expected": 0}}`.