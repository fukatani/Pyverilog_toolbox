module TOP(CLK, RST, WRITE, WRITE_DATA);
  input CLK,RST,WRITE;
  input [2:1] WRITE_DATA;
  reg [4:3] reg0;


  always @(posedge CLK) begin
    if(WRITE) begin
      reg0[4:3] <= WRITE_DATA[2:1];
    end
  end

endmodule

