module checker( input [7:0]addr , input wr, input [7:0]data , output reg [6:0]F_chk , output reg [4:0]sum_chk );

  always @(*) begin
    if (wr && (addr == 8'hf8) && (data == 8'h01)) F_chk[0] = 1;   else F_chk[0] = 0;  
    if (wr && (addr == 8'hf9) && (data == 8'h01)) F_chk[1] = 1;   else F_chk[1] = 0;  
    if (wr && (addr == 8'hfA) && (data == 8'h02)) F_chk[2] = 1;   else F_chk[2] = 0;  
    if (wr && (addr == 8'hfB) && (data == 8'h03)) F_chk[3] = 1;   else F_chk[3] = 0;  
    if (wr && (addr == 8'hfC) && (data == 8'h05)) F_chk[4] = 1;   else F_chk[4] = 0;  
    if (wr && (addr == 8'hfD) && (data == 8'h08)) F_chk[5] = 1;   else F_chk[5] = 0;  
    if (wr && (addr == 8'hfE) && (data == 8'h0D)) F_chk[6] = 1;   else F_chk[6] = 0;  
    if (wr && (addr == 8'hf2) && (data == 8'h02)) sum_chk[0] = 1; else sum_chk[0] = 0;
    if (wr && (addr == 8'hf2) && (data == 8'h03)) sum_chk[1] = 1; else sum_chk[1] = 0;
    if (wr && (addr == 8'hf2) && (data == 8'h05)) sum_chk[2] = 1; else sum_chk[2] = 0;
    if (wr && (addr == 8'hf2) && (data == 8'h08)) sum_chk[3] = 1; else sum_chk[3] = 0;
    if (wr && (addr == 8'hf2) && (data == 8'h0D)) sum_chk[4] = 1; else sum_chk[4] = 0;
  end
endmodule