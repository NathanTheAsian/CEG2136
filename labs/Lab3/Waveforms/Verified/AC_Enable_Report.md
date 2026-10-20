# 4-bit arithmetic enable test

Tested 4096 combinations: 256 A/B pairs, 8 operations, both E levels.

Data enable checks compare E=0 with zero, and E=1 with the existing internal operand-selection and ADD/SUB behavior. They do not certify the internal arithmetic against the lab table.

Data enable failures: 0.
Disabled OV high cases: 256.
Disabled C_out high cases: 1024.

OV and C_out are directly connected to the adder and are not gated by E.

Waveforms are named 4bitArithmeticCircuit_E0_S000test.vwf etc., in this folder.