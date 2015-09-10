module TOP(CLK, RSTN);
  input CLK, RSTN;

  reg [2:0] up_cnt;

  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt <= 0;
    end else if(up_cnt2 == 3'd6) begin
      up_cnt <= 0;
    end else begin
      up_cnt <= up_cnt + 1;
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
    end
  end
endmodule

