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
pip install pyverilo_toolbox
```

Python 3.x is not tried by author.


Usage
==============================

## codeclone_finder
codeclone_finder can find pair of the register clone, which always hold same value.
Also can find pair of the invert register, which always hold different value.

After install Pyverilog_toolbox, you can use codeclone_finder by this command.

```
python codeclone_finder.py xxxx.v
```

ex.
Input verilog file:

```
  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

  assign in1 = IN;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg2 <= 1'b0;
    end else begin
      reg2 <= in1;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg3 <= 1'b1;
    end else begin
      reg3 <= !IN;
    end
  end
```

Output:

```
Invert reg pairs: [((TOP.reg1, 0), (TOP.reg3, 0)), ((TOP.reg2, 0), (TOP.reg3, 0))]
Clone reg pairs: [((TOP.reg1, 0), (TOP.reg2, 0))]
```

You can refine this RTL as follows(by manual) for circuit size and maintainability.

```
  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

  wire reg2 = reg1;
  wire reg3 = !reg1;

```

## regmap_analyzer

regmap_analyzer can analyze register map structure from RTL.
After install Pyverilog_toolbox, you can use regmap analyzer by this command.

```
python regmap_analyzer.py xxxx.v -S config.txt
```


xxxx.v is regmap RTL file.
To analyse register map, config file is needed.

control flag is to be defined in config file.
testcode/regmap.v is example of register map RTL file,
and testcode/setup.txt is example of config file.

Analysis result will be output as out.csv.

ex.

Input verilog file:
```
  always @(posedge CLK) begin
    if(RST) begin
      reg0[1:0] <= 0;
      reg1 <= 0;
    end else if(WRITE) begin
      case(ADDR)
        0:reg0[1:0] <= WRITE_DATA;
        1:reg1 <= WRITE_DATA[0];
      endcase
    end
  end

  always @* begin
    case(ADDR)
      0:READ_DATA[1:0] = reg0[1:0];
      1:READ_DATA[1:0] = {1'b0,reg1};
    endcase
  end
```

Output:

```
Write Map		
ADD	1	0
0	TOP.reg0[1]	TOP.reg0[0]
1		TOP.reg1[0]
Read Map		
ADD	1	0
0	TOP.reg0[1]	TOP.reg0[0]
1		TOP.reg1[0]
```


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