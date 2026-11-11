# Active Lab 3 functional verification

Compiled the BDF sources listed by labs/Lab3/Lab3.qsf, captured in source_hashes.json.
Functional simulation uses an isolated Cyclone III project for the legacy Quartus simulator; no board timing or hardware is validated.
All 4096 A/B/S combinations are covered. C is sampled after the input/output register pipeline settles.

Result: 4096/4096 result-word cases passed.
Missing status outputs: .

| S | Operation | Correct C / 256 |
|---|---|---:|
| 0000 | A + B | 256 |
| 0001 | A + B + 1 | 256 |
| 0010 | A | 256 |
| 0011 | A + 1 | 256 |
| 0100 | A - B - 1 | 256 |
| 0101 | A - B | 256 |
| 0110 | ~A | 256 |
| 0111 | -A | 256 |
| 1000 | 0 | 256 |
| 1001 | 15 | 256 |
| 1010 | A & B | 256 |
| 1011 | A &#124; B | 256 |
| 1100 | A ^ B | 256 |
| 1101 | A & ~B | 256 |
| 1110 | arithmetic shift left A | 256 |
| 1111 | arithmetic shift right A | 256 |

## First failure for each operation


Reset checks: [{"wave": "TopTest_A0-15_B0-15_S0000-0011.vwf", "C_at_1ns": 0, "C_at_19ns": 0}, {"wave": "TopTest_A0-15_B0-15_S0100-0111.vwf", "C_at_1ns": 0, "C_at_19ns": 0}, {"wave": "TopTest_A0-15_B0-15_S1000-1011.vwf", "C_at_1ns": 0, "C_at_19ns": 0}, {"wave": "TopTest_A0-15_B0-15_S1100-1111.vwf", "C_at_1ns": 0, "C_at_19ns": 0}]
Output settling differences after the second rising edge: 0.
