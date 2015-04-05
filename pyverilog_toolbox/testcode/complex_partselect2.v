module TOP(CLK, RST, WRITE, READ, READ_DATA);
  input CLK,RST,WRITE,READ;
  output reg [1:0] READ_DATA;
  reg [4:3] reg0;

  always @* begin
    READ_DATA[1:0] = reg0[4:3];
  end

endmodule

