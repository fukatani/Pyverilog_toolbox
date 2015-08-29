module TOP(CLK, RST);
  input CLK, RST;
  reg reg1;
  reg reg2;
  wire in1; //floating

  always @(posedge CLK or negedge RST) begin
    if(!RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= in1;
    end
  end

endmodule


