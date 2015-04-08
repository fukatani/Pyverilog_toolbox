module TOP(CLK, RSTN, UP_ENABLE);
  input CLK,RSTN,UP_ENABLE;

  reg [2:0] up_cnt;

  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt <= 0;
    end else if(UP_ENABLE) begin
      up_cnt <= up_cnt + 2'd1;
    end else begin
      up_cnt <= up_cnt;
    end
  end

endmodule

