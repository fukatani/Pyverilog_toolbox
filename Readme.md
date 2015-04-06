Introduction
==============================
Pyverilog_toolbox is Pyverilog-based verification/design tool.

Accerating your digital circuit design verification.


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

Python 3.x is not tried by author.


Usage
==============================

ÅEregmap_analyzer

After install, you can use regmap analyzer by this command.

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

Output
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


ÅEcombloop_finder
```
python regmap_combloop_finder.py xxxx.v
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

License
==============================

Apache License 2.0
(http://www.apache.org/licenses/LICENSE-2.0)


Copyright
==============================

Copyright (C) 2015, Ryosuke Fukatani