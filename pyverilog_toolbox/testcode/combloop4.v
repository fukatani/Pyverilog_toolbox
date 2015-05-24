module TOP(CLK, RST);
  input CLK,RST;
  wire a1,wire1,wire2,wire3,z1;

  assign a1 = wire1;
  assign wire1 = wire2;
  assign wire2 = !wire3;
  assign wire3 = wire1;
  assign z1 = wire1;

endmodule

