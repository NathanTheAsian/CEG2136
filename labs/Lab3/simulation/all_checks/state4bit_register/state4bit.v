// Lab 3, section 3.3: combinational status logic.
// F3..F0 are the selected ALU result BEFORE its output register.
// S3 = 0 selects arithmetic; S3 = 1 selects logic/shift.
// CAR2 is the carry OUT of bit 2 (INTO bit 3).
// CAR3 is the carry OUT of bit 3. Neither input is a result bit.
module state4bit (
    input wire F3, F2, F1, F0,
    input wire S3,
    input wire CAR2, CAR3,
    output wire V, Z, N, Cy
);
    assign V  = ~S3 & (CAR2 ^ CAR3);
    assign Z  = ~(|{F3, F2, F1, F0});
    assign N  = F3;
    assign Cy = ~S3 & CAR3;
endmodule
