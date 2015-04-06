module TOP(CLK, RST);
  input CLK,RST;
  wire wire1,wire2,wire3;

  assign wire1 = wire3;

  SUB sub(wire1, !wire2, wire3);

endmodule


module SUB(wire1, wire2, wire3);

  input wire1, wire2;
  output wire3;
  assign wire3 = wire2;
  assign wire2 = wire1;

endmodule