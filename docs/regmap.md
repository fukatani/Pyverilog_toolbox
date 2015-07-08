## REGMAP_ANALYZER USAGE

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

