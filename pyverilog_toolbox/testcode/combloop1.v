module TOP(CLK, RST);
  input CLK,RST;
  wire wire1,wire2,wire3;

  assign wire1 = wire2;
  assign wire2 = !wire3;
  assign wire3 = wire1;

endmodule

