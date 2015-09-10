[![Build Status](https://travis-ci.org/fukatani/Pyverilog_toolbox.svg?branch=master)](https://travis-ci.org/fukatani/Pyverilog_toolbox)

Introduction
==============================
Pyverilog_toolbox is Pyverilog-based verification/design tool including code clone finder, metrics calculator and so on.
Pyverilog_toolbox accerating your digital circuit design verification.
Thanks to Pyverilog developer shtaxxx.


Software Requirements
==============================
* Python (2.7)
* Pyverilog (you can download from https://github.com/shtaxxx/Pyverilog)
Pyverilog requires Icarus verilog


Installation
==============================

(If you want to use GUI stand alone version for windows, [Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/gui.md)

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


Features
==============================

## codeclone_finder
codeclone_finder can find pair of the register clone, which always hold same value.
Also can find pair of the invert register, which always hold different value.

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/codeclone.md "codeclone_finder")

## combloop_finder

Combinational logic loop is sticky problem, but you can find it by combloop_finder easily.

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/combloop.md "combloop_finder")


## unreferenced_finder

Unreferenced_finder can find signals which isn't referenced by any signals.
Also floating nodes can be found.
By using this, you can delte unnecessary codes.

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/unreferenced.md "unreferenced_finder")

##metrics_calculator

metrics_analyzer is metrics measurment tools for Verilog HDL.
You can visualize complecity of module/register/function/.

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/metrics.md "metrics_analyzer")

## regmap_analyzer

regmap_analyzer can analyze register map structure from RTL.

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/regmap.md "regmap_analyzer")

## cnt_analyzer

cnt_analyzer analyze counter property(up or down, max value, reset value and counter dependency).
And extracting event which depends on counter value.
This feature help you finding redundunt counter, deadlock loop, and other counter trouble. 

[Click here to get detail](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/cnt_analyzer.md "cnt_analyzer")

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