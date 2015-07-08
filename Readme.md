Introduction
==============================
Pyverilog_toolbox is Pyverilog-based verification/design tool.

Accerating your digital circuit design verification.

Thanks to Pyverilog developer shtaxxx.


Software Requirements
==============================
* Python (2.7)
* Pyverilog (you can download from https://github.com/shtaxxx/Pyverilog)


Installation
==============================

If you want to use Pyverilog as a general library, you can install on your environment by using setup.py. 

If you use Python 2.7,

```
python setup.py install
```

Or you can use pip
```
pip install pyverilog_toolbox
```

Python 3.x is not tried by author.


Tools
==============================

## codeclone_finder
codeclone_finder can find pair of the register clone, which always hold same value.
Also can find pair of the invert register, which always hold different value.

[usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/codeclone.md "codeclone_finder")

## regmap_analyzer

regmap_analyzer can analyze register map structure from RTL.
After install Pyverilog_toolbox, you can use regmap analyzer by this command.

[usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/regmap.md "regmap_analyzer")

## combloop_finder

Combinational logic loop is sticky problem, but you can find it by combloop_finder easily.



```
python combloop_finder.py xxxx.v
```

if there is a combinational loop in your design, combloop_finder raise error and specify loop occurrence place.

ex.

```
module TOP(CLK, RST);
  input CLK,RST;
  wire wire1,wire2,wire3;

  assign wire1 = wire2;
  assign wire2 = !wire3;
  assign wire3 = wire1;

endmodule
```


Output:
```
CombLoopException: Combinational loop is found @TOP.wire3
```

## cnt_analyzer

cnt_analyzer analyze counter property(up or down, max value, reset value and counter dependency).
And extracting event which depends on counter value.
This feature help you finding redundunt counter, deadlock loop, and other counter trouble. 


```
python cnt_analyzer.py xxxx.v
```

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

License
==============================

Apache License 2.0
(http://www.apache.org/licenses/LICENSE-2.0)


Copyright
==============================

Copyright (C) 2015, Ryosuke Fukatani

Related Project and Site
==============================

Pyverilog
https://github.com/shtaxxx/Pyverilog

Blog entry(in Japanese)
http://segafreder.hatenablog.com/entry/2015/05/23/161000