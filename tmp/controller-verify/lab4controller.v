// Copyright (C) 1991-2013 Altera Corporation
// Your use of Altera Corporation's design tools, logic functions 
// and other software and tools, and its AMPP partner logic 
// functions, and any output files from any of the foregoing 
// (including device programming or simulation files), and any 
// associated documentation or information are expressly subject 
// to the terms and conditions of the Altera Program License 
// Subscription Agreement, Altera MegaCore Function License 
// Agreement, or other applicable license agreement, including, 
// without limitation, that your use is for the sole purpose of 
// programming logic devices manufactured by Altera and sold by 
// Altera or its authorized distributors.  Please refer to the 
// applicable agreement for further details.

// PROGRAM		"Quartus II 64-Bit"
// VERSION		"Version 13.0.1 Build 232 06/12/2013 Service Pack 1 SJ Web Edition"
// CREATED		"Mon Nov 16 14:56:34 2026"

module lab4controller(
	IR7,
	T12,
	T0,
	T4,
	T2,
	T1,
	T3,
	T8,
	T6,
	T5,
	T7,
	T10,
	T9,
	T11,
	Stop,
	DR0,
	DR4,
	DR3,
	DR2,
	DR1,
	DR7,
	DR6,
	DR5,
	IR0,
	IR1,
	IR2,
	IR3,
	IR4,
	IR5,
	IR6,
	Halt,
	SC_Clear,
	BusSel1,
	BusSel2,
	ALU_Sel0,
	BusSel0,
	ALU_Sel2,
	OUTD_Load,
	AC_Inc,
	ALU_Sel1,
	AC_Clear,
	IR_Load,
	DR_Inc,
	AC_Load,
	DR_Load,
	AR_Load,
	PC_Load,
	PC_Inc,
	memwrite
);


input wire	IR7;
input wire	T12;
input wire	T0;
input wire	T4;
input wire	T2;
input wire	T1;
input wire	T3;
input wire	T8;
input wire	T6;
input wire	T5;
input wire	T7;
input wire	T10;
input wire	T9;
input wire	T11;
input wire	Stop;
input wire	DR0;
input wire	DR4;
input wire	DR3;
input wire	DR2;
input wire	DR1;
input wire	DR7;
input wire	DR6;
input wire	DR5;
input wire	IR0;
input wire	IR1;
input wire	IR2;
input wire	IR3;
input wire	IR4;
input wire	IR5;
input wire	IR6;
output wire	Halt;
output wire	SC_Clear;
output wire	BusSel1;
output wire	BusSel2;
output wire	ALU_Sel0;
output wire	BusSel0;
output wire	ALU_Sel2;
output wire	OUTD_Load;
output wire	AC_Inc;
output wire	ALU_Sel1;
output wire	AC_Clear;
output wire	IR_Load;
output wire	DR_Inc;
output wire	AC_Load;
output wire	DR_Load;
output wire	AR_Load;
output wire	PC_Load;
output wire	PC_Inc;
output wire	memwrite;

wire	DR_zero;
wire	High;
wire	Immediate_DR;
wire	Indirect_AR;
wire	IR0_n;
wire	IR1_n;
wire	IR5_n;
wire	IR6_n;
wire	IR7_n;
wire	LDD_Load;
wire	Low;
wire	Memory_DR;
wire	net_inst20;
wire	net_inst25;
wire	net_inst30;
wire	net_inst31;
wire	net_inst33;
wire	net_inst37;
wire	net_inst40;
wire	net_inst43;
wire	net_inst47;
wire	net_inst50;
wire	net_inst51;
wire	net_inst52;
wire	net_inst55;
wire	net_inst73;
wire	net_inst74;
wire	net_inst75;
wire	PC_Load_ALTERA_SYNTHESIZED;
wire	Register_Exec;
wire	Stop_n;
wire	X0;
wire	X1;
wire	X2;
wire	Y0;
wire	Y1;
wire	Y2;
wire	Y3;
wire	Y4;
wire	Y5;
wire	Y6;
wire	Y7;
wire	SYNTHESIZED_WIRE_0;
wire	SYNTHESIZED_WIRE_1;
wire	SYNTHESIZED_WIRE_2;
wire	SYNTHESIZED_WIRE_3;
wire	SYNTHESIZED_WIRE_4;
wire	SYNTHESIZED_WIRE_5;
wire	SYNTHESIZED_WIRE_6;
wire	SYNTHESIZED_WIRE_7;
wire	SYNTHESIZED_WIRE_8;
wire	SYNTHESIZED_WIRE_9;
wire	SYNTHESIZED_WIRE_10;
wire	SYNTHESIZED_WIRE_11;
wire	SYNTHESIZED_WIRE_12;
wire	SYNTHESIZED_WIRE_13;
wire	SYNTHESIZED_WIRE_14;
wire	SYNTHESIZED_WIRE_15;
wire	SYNTHESIZED_WIRE_16;
wire	SYNTHESIZED_WIRE_17;
wire	SYNTHESIZED_WIRE_18;

assign	OUTD_Load = T1;
assign	IR_Load = T3;





assign	IR7_n =  ~IR7;

assign	IR6_n =  ~IR6;

assign	Y3 = IR7_n & IR2;

assign	Y4 = IR7_n & IR3;

assign	Y5 = IR7_n & IR4;

assign	Y6 = IR7_n & IR5;

assign	Y7 = ~(IR0 | IR2 | IR1 | IR3 | IR5 | IR4);

assign	SYNTHESIZED_WIRE_1 = T9 & Y4;

assign	SYNTHESIZED_WIRE_0 = T10 & Y6;

assign	memwrite = SYNTHESIZED_WIRE_0 | SYNTHESIZED_WIRE_1;


or5_0	b2v_inst19(
	.IN1(T0),
	.IN3(net_inst25),
	.IN2(net_inst20),
	.IN5(Indirect_AR),
	.IN4(T2),
	.OUT(AR_Load));

assign	IR0_n =  ~IR0;

assign	net_inst20 = T5 & IR7_n;

assign	SYNTHESIZED_WIRE_2 = DR7 | DR5 | DR6 | DR4 | DR2 | DR3 | DR1 | DR0;

assign	DR_zero =  ~SYNTHESIZED_WIRE_2;

assign	Stop_n =  ~Stop;

assign	net_inst25 = T6 & IR7_n;

assign	PC_Load_ALTERA_SYNTHESIZED = T8 & Y5;

assign	PC_Inc = SYNTHESIZED_WIRE_3 | net_inst30 | net_inst31 | SYNTHESIZED_WIRE_4;

assign	SYNTHESIZED_WIRE_3 = T2 & Stop_n;

assign	SYNTHESIZED_WIRE_4 = T5 & IR7_n & Stop_n;


assign	net_inst30 = T11 & Y6 & DR_zero & Stop_n;

assign	net_inst31 = T12 & Y6 & DR_zero & Stop_n;

assign	DR_Load = Immediate_DR | Memory_DR;


or5_1	b2v_inst33(
	.IN1(Y0),
	.IN3(Y2),
	.IN2(Y1),
	.IN5(Y6),
	.IN4(Y3),
	.OUT(net_inst33));

assign	DR_Inc = T9 & Y6;

assign	AC_Clear = T5 & X2 & IR0;

assign	SYNTHESIZED_WIRE_5 = IR2 | IR3 | IR1;

assign	net_inst37 = SYNTHESIZED_WIRE_5 & Register_Exec;

assign	Register_Exec = T5 & X2;

assign	SYNTHESIZED_WIRE_6 = Y0 | Y2 | Y3 | Y1;

assign	X1 = IR7_n & IR6;

assign	net_inst40 = SYNTHESIZED_WIRE_6 & T9;

assign	AC_Load = net_inst40 | LDD_Load | net_inst37;

assign	AC_Inc = T5 & X2 & IR4;

assign	net_inst43 = Y3 | Y0;

assign	SYNTHESIZED_WIRE_8 = net_inst43 & T9;

assign	SYNTHESIZED_WIRE_7 = T5 & X2 & IR1;

assign	net_inst47 = SYNTHESIZED_WIRE_7 | SYNTHESIZED_WIRE_8;

assign	LDD_Load = T8 & Y7;

assign	ALU_Sel2 = LDD_Load | net_inst47;

assign	IR1_n =  ~IR1;

assign	net_inst50 = T9 & Y3;

assign	net_inst51 = net_inst52 & T5 & X2;

assign	net_inst52 = IR2 | IR3 | IR1;

assign	ALU_Sel1 = net_inst51 | LDD_Load | net_inst50;

assign	Indirect_AR = T7 & X1;

assign	net_inst55 = Y2 & T9;

assign	Memory_DR = net_inst33 & T8;

assign	SYNTHESIZED_WIRE_9 = IR1 | IR3;

assign	SYNTHESIZED_WIRE_11 = SYNTHESIZED_WIRE_9 & SYNTHESIZED_WIRE_10;

assign	SYNTHESIZED_WIRE_10 = T5 & X2;

assign	X2 = IR7 & IR6_n;

assign	ALU_Sel0 = SYNTHESIZED_WIRE_11 | net_inst55;

assign	BusSel2 = T0 | SYNTHESIZED_WIRE_12;

assign	SYNTHESIZED_WIRE_12 = T9 & Y4;

assign	BusSel1 = T0 | SYNTHESIZED_WIRE_13 | SYNTHESIZED_WIRE_14 | T2;

assign	SYNTHESIZED_WIRE_13 = T5 & IR7_n;

assign	SYNTHESIZED_WIRE_14 = T10 & Y6;

assign	BusSel0 = Immediate_DR | SYNTHESIZED_WIRE_15 | SYNTHESIZED_WIRE_16 | SYNTHESIZED_WIRE_17;

assign	Immediate_DR = T7 & Y7;

assign	SYNTHESIZED_WIRE_17 = T8 & Y5;


assign	Y0 = IR7_n & IR1_n & IR0;

assign	SYNTHESIZED_WIRE_15 = T9 & Y4;

assign	SYNTHESIZED_WIRE_16 = T10 & Y6;


or5_2	b2v_inst72(
	.IN1(Y0),
	.IN3(Y2),
	.IN2(Y1),
	.IN5(Y4),
	.IN4(Y3),
	.OUT(SYNTHESIZED_WIRE_18));

assign	net_inst73 = SYNTHESIZED_WIRE_18 & T9;

assign	net_inst74 = T8 & Y7;

assign	net_inst75 = T12 & Y6;


or5_3	b2v_inst76(
	.IN1(net_inst73),
	.IN3(net_inst74),
	.IN2(net_inst75),
	.IN5(PC_Load_ALTERA_SYNTHESIZED),
	.IN4(Register_Exec),
	.OUT(SC_Clear));

assign	Halt = T5 & X2 & IR5;

assign	Y1 = IR7_n & IR1 & IR0_n;

assign	Y2 = IR7_n & IR1 & IR0;

assign	PC_Load = PC_Load_ALTERA_SYNTHESIZED;
assign	High = 1;
assign	Low = 0;

endmodule

module or5_0(IN1,IN3,IN2,IN5,IN4,OUT);
/* synthesis black_box */

input IN1;
input IN3;
input IN2;
input IN5;
input IN4;
output OUT;

endmodule

module or5_1(IN1,IN3,IN2,IN5,IN4,OUT);
/* synthesis black_box */

input IN1;
input IN3;
input IN2;
input IN5;
input IN4;
output OUT;

endmodule

module or5_2(IN1,IN3,IN2,IN5,IN4,OUT);
/* synthesis black_box */

input IN1;
input IN3;
input IN2;
input IN5;
input IN4;
output OUT;

endmodule

module or5_3(IN1,IN3,IN2,IN5,IN4,OUT);
/* synthesis black_box */

input IN1;
input IN3;
input IN2;
input IN5;
input IN4;
output OUT;

endmodule
