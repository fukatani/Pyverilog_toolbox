module TOP(CLK, RSTN, UP_ENABLE, UP_ENABLE2, CLEAR);
  input CLK,RSTN,UP_ENABLE,UP_ENABLE2,CLEAR;

  reg [2:0] up_cnt;

  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt <= 0;
    end else if(up_cnt == 3'd6) begin
      up_cnt <= 0;
    end else if(CLEAR) begin
      up_cnt <= 0;
    end else if(UP_ENABLE) begin
      up_cnt <= up_cnt + 3'd1;
    end else if(UP_ENABLE2) begin
      up_cnt <= up_cnt + 3'd1;
    end else begin
      up_cnt <= up_cnt;
    end
  end

endmodule

