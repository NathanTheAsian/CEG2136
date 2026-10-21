# Exhaustive top-level waveforms

Each file contains 1024 unique (A,B,S) combinations. Together the four files cover all 4096 combinations exactly once.

| File | S3..S0 selectors | A and B |
|---|---|---|
| TopTest_A0-15_B0-15_S0000-0011.vwf | 0000 through 0011 | All 256 pairs per selector |
| TopTest_A0-15_B0-15_S0100-0111.vwf | 0100 through 0111 | All 256 pairs per selector |
| TopTest_A0-15_B0-15_S1000-1011.vwf | 1000 through 1011 | All 256 pairs per selector |
| TopTest_A0-15_B0-15_S1100-1111.vwf | 1100 through 1111 | All 256 pairs per selector |

CLK has a 10 ns period. CLRN is low for 0�20 ns and high thereafter. Each input vector lasts 40 ns (four rising edges), starting at 20 ns. Total duration per file: 40980 ns. Check outputs 36 ns after each vector starts, after the register pipeline settles. Bit 0 is the least significant bit. Output stimulus is X; run simulation to obtain actual outputs. These files supply exhaustive inputs; they do not assert that the circuit passes.





Simulation results: ../Results/. Current reports: ../../Reports/.
