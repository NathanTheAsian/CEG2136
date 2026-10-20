// Combines the lab's state4bit logic and following four D flip-flops.
// Use the same clock and active-low asynchronous clear as result register C.
module state4bit_register (
    input wire CLK, CLRN,
    input wire F3, F2, F1, F0,
    input wire S3,
    input wire CAR2, CAR3,
    output reg V, Z, N, Cy
);
    wire next_V, next_Z, next_N, next_Cy;

    state4bit status_logic (
        .F3(F3), .F2(F2), .F1(F1), .F0(F0),
        .S3(S3), .CAR2(CAR2), .CAR3(CAR3),
        .V(next_V), .Z(next_Z), .N(next_N), .Cy(next_Cy)
    );

    always @(posedge CLK or negedge CLRN) begin
        if (!CLRN)
            {Cy, N, Z, V} <= 4'b0000;
        else
            {Cy, N, Z, V} <= {next_Cy, next_N, next_Z, next_V};
    end
endmodule
