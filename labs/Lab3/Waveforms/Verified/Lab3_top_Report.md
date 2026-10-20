# Lab3_top functional test

All 4096 A/B/selector combinations tested. Clock: pin_name1. Each vector is held for two rising edges to accommodate the input and output registers.

Reference: Lab3 PDF Tables 1 and 2. V is zero for logic/shift operations (optional shift overflow omitted). Carry is the carry out of op0 + op1 + S0 for arithmetic, zero for logic.

| S | Passing / 256 | Result failures | V failures | Z failures | N failures | Cy failures |
|---|---:|---:|---:|---:|---:|---:|
| 0000 | 0 | 0 | 0 | 240 | 0 | 256 |
| 0001 | 0 | 256 | 128 | 240 | 128 | 128 |
| 0010 | 0 | 0 | 0 | 240 | 0 | 256 |
| 0011 | 0 | 256 | 16 | 240 | 32 | 16 |
| 0100 | 0 | 0 | 0 | 240 | 0 | 256 |
| 0101 | 0 | 256 | 128 | 240 | 128 | 128 |
| 0110 | 0 | 0 | 0 | 240 | 0 | 256 |
| 0111 | 0 | 256 | 16 | 240 | 32 | 16 |
| 1000 | 0 | 256 | 64 | 0 | 0 | 120 |
| 1001 | 0 | 256 | 64 | 256 | 0 | 136 |
| 1010 | 27 | 211 | 0 | 175 | 0 | 0 |
| 1011 | 0 | 255 | 0 | 255 | 0 | 256 |
| 1100 | 8 | 240 | 64 | 240 | 0 | 120 |
| 1101 | 1 | 225 | 64 | 175 | 64 | 136 |
| 1110 | 0 | 240 | 0 | 224 | 128 | 0 |
| 1111 | 0 | 240 | 0 | 224 | 128 | 256 |

Overall: 36/4096 complete cases pass.

Waveforms: Lab3_top_S0000test.vwf through Lab3_top_S1111test.vwf. The existing user waveform was also run and saved as Lab3_top_existingtest.vwf.

Detailed vectors, expected outputs, actual outputs and compiler/simulation logs: simulation/all_checks/Lab3_top/.

Source files changed during test: []

## Compilation

The main Lab3 project compiled successfully with 0 errors and 13 warnings. The source files were unchanged throughout the test. No circuit files were modified by this test run.

## Wiring faults found

1. Cy: XOR inst11 receives NOT S3 and arithmetic C_out. It must be an AND to implement Cy = NOT S3 AND C_out. For example, 0+0 currently produces Cy=1.
2. Z: NAND8 inst12 is incorrect for zero detection. Since one enabled-bank counterpart is zero, this NAND is effectively always high. Use NOR over the selected four result bits (or NOR8 over the mutually exclusive enabled arithmetic/logic outputs).
3. Result MUX logic inputs (D0) are misaligned. Set inst20.D0=CI3, inst21.D0=CI2, inst22.D0=CI1, inst23.D0=CI0. Currently they receive CA0, CI3, CI2, CI1 respectively. Keep their D1 inputs connected to CA3, CA2, CA1, CA0 and S connected to NOT S3.
4. V: status input is connected directly to arithmetic OV. Gate it with NOT S3 so logic operations do not inherit arithmetic overflow.
5. The existing arithmetic carry-in/ADD-SUB issue remains: the arithmetic block drives FourBitAdder.M with S0, causing both B inversion and carry-in. This fails odd arithmetic operation codes.
6. The logic block still inherits its mask and selector faults, and its ASL/ASR inputs are unconnected at top level. For the lab's arithmetic shifts, connect ASL to 0 and ASR to registered A3, with internal bit-neighbor routing matching the lab operation table.

The top has no external clear input: register CLRN pins are unconnected. The test therefore fills the input/output pipeline with two clock edges before checking results; reset behavior of the full top was not tested.
