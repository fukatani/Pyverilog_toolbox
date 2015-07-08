## combloop_finder usage

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