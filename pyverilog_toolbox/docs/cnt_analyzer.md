## cnt_analyzer usage

cnt_analyzer analyze counter property(up or down, max value, reset value and counter dependency).
And extracting event which depends on counter value.
This feature help you finding redundunt counter, deadlock loop, and other counter trouble. 


```
python cnt_analyzer.py xxxx.v
```

ex.
Input verilog file:
```
module TOP(CLK, RSTN, UP_ENABLE, UP_ENABLE2, CLEAR);
  input CLK,RSTN,UP_ENABLE,UP_ENABLE2,CLEAR;

  reg [2:0] up_cnt;
  wire is_count_max = up_cnt == 3'd6;

  always @(posedge CLK or negedge RSTN) begin
    if(!RSTN) begin
      up_cnt <= 0;
    end else if(is_count_max) begin
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
    end
  end

endmodule



```
Output:
```
name: TOP.up_cnt
category: up counter
reset val: 0
max_val: 6
mother counter:set([])

name: TOP.down_cnt
category: down counter
reset val: 0
max_val: 4
mother counter:set([])

name: TOP.up_cnt2
category: up counter
reset val: 0
max_val: 4
mother counter:set(['TOP.up_cnt'])

TOP.up_cnt {2: ["TOP.now='d1 @(TOP_up_cnt==3'd2)", "TOP.is_count_max='d1 @(TOP_up_cnt==3'd2)", "TOP.up_cnt2='d0 @(TOP_up_cnt==3'd2)"]}
TOP.down_cnt {}
TOP.up_cnt2 {}
```
