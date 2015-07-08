## unreferenced finder usage

Unreferenced_finder can find signals which isn't referenced by any signals.
By using this, you can delte unnecessary codes.

```
python unrefereced_finder.py xxxx.v
```


xxxx.v is regmap RTL file.

ex.

Input verilog file:
```
module TOP(CLK, RST, IN, IN2, reg1, OUT);
  input CLK, RST, IN, IN2;
  reg reg1,reg2,reg3;
  output reg1,OUT;
  wire in1;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg2 <= 1'b0;
    end else begin
      reg2 <= reg1;
    end
  end

  SUB sub(CLK,RST,in1,OUT);
endmodule

module SUB(CLK,RST,IN, OUT);
  input CLK, RST, IN;
  output OUT;
  reg reg1;
  wire OUT = reg1;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= 1'b1;
    end
  end

endmodule

```

Output:

```
finded unreferenced variables: ['TOP.reg2', 'TOP.IN2', 'TOP.reg3', 'TOP.sub.IN']
```

