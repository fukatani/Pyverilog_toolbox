module TOP(CLK, RSTN);
  input CLK;
  input [2:1] RSTN;
  reg reg1;

  always @(posedge CLK or negedge RSTN[1]) begin
    if(!RSTN[1]) begin
      reg1 <= 0;
    end else begin
      reg1 <= reg1;
    end
  end

endmodule

