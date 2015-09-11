module TOP(CLK, RSTN, UP_ENABLE, UP_ENABLE2, CLEAR);
  input CLK,RSTN,UP_ENABLE,UP_ENABLE2,CLEAR;

  reg [2:0] up_cnt;
  wire is_cnt_four = up_cnt == 4;

  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt <= 0;
    end else if(up_cnt >= 3'd5) begin
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

  reg [2:0] up_cnt2;
  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt2 <= 0;
    end else if(up_cnt2 != 3'd5 && up_cnt == 3'd5) begin
      up_cnt2 <= up_cnt2 + 3'd1;
    end else begin
      up_cnt2 <= 0;
    end
  end

  reg [2:0] down_cnt;
  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      down_cnt <= 0;
    end else if(down_cnt != 3'd0) begin
      down_cnt <= down_cnt - 3'd1;
    end else begin
      down_cnt <= 3'd5;
    end
  end

  reg now;
  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      now <= 0;
    end else if(up_cnt == 3'd4) begin
      now <= 0;
    end else if(up_cnt == 3'd2) begin
      now <= 1;
    end else if((up_cnt == 2) && (up_cnt2 == 2)) begin
      now <= 1;
    end
  end

endmodule

