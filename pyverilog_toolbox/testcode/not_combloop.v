module TOP(CLK, RST);
  input CLK,RST;
  reg reg1;

  always @(posedge CLK or negedge RSTN) begin
    if(RST) begin
      reg1 <= 0;
    end else begin
      reg1 <= reg1;
    end
  end

endmodule

