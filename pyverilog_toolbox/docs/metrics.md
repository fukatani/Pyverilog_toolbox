## metrics_analyzer usage

metrics_analyzer is metrics measurment tools for Verilog HDL.
You can visualize complecity of module/register/function/.

```
python metrics_analyzer.py xxxx.v
```

Each metrics is calculated as described below.

(COEF_FOR_XXXX * XXXX) ^ POW_OF_XXXX

Parameters corresponding to XXXX is different by each of metrics (module/register/function).


# module metrics arguments
Number of input port in each module.

Number of output port in each module.

Number of register in each module.

Number of clock in each module.

Number of reset in each module.

# register metrics arguments
Number of condition branch in each register.

Max nest of control syntax in each register.

# function metrics arguments
Number of condition branch in each function.

Max nest of control syntax in each function.

Number of arguments in each function.


ex.
Input verilog file:
```

module TOP(CLK, RST, IN, IN2);
  input CLK, RST, IN, IN2;
  reg reg2;

  always @(posedge CLK or negedge RST) begin
      reg2 <= func1(IN,IN2);
  end
  function func1;
    input bit;
    input bit2;

      if(bit2)
        func1 = !bit;
      else
        func1 = bit;

  endfunction

endmodule


```
Output:
```
module metrics total: 19

each score:
TOP: 19
Number of input ports: 4
Number of output ports: 0
Number of registers:  1
Number of clocks: 1
Number of resets:  1


register metrics total: 1

each score:
('TOP', 0): 1
Number of branch: 0
Max nest: 1


function metrics total: 9

each score:
('TOP.md_always0.al_block0.al_functioncall0', 0): 9
Number of branch: 1
Max nest: 2
Number of variables: 2
```


You can use configure parameters for metrics calculation.

```
python metrics_analyzer.py xxxx.v -S yyy.txt
```


yyy.txt sample:
```
#config parameters for module metrics
COEF_FOR_INPUT:1
POW_FOR_INPUT:2
COEF_FOR_OUTPUT:1
POW_FOR_OUTPUT:2
COEF_FOR_REG:1
POW_FOR_REG:1
COEF_FOR_CLK:1
POW_FOR_CLK:1
COEF_FOR_RST:1
POW_FOR_RST:1

#config parameters for module metrics
COEF_FOR_BRANCH':
POW_FOR_BRANCH':
COEF_FOR_NEST':
POW_FOR_NEST':

#config parameters for function metrics
COEF_FOR_VAR':
NEST_FOR_VAR':

#config parameters for display
MODULE_DISP_LIMIT':
REG_DISP_LIMIT':
FUNC_DISP_LIMIT':
```

You may write only parameter which you want to change from default parameter.