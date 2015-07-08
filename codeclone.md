##USAGE

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

