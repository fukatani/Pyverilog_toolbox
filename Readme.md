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

[Click here to know usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/codeclone.md "codeclone_finder")

## regmap_analyzer

regmap_analyzer can analyze register map structure from RTL.
After install Pyverilog_toolbox, you can use regmap analyzer by this command.

[Click here to know usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/regmap.md "regmap_analyzer")

## combloop_finder

Combinational logic loop is sticky problem, but you can find it by combloop_finder easily.

[Click here to know usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/combloop.md "combloop_finder")

## cnt_analyzer

cnt_analyzer analyze counter property(up or down, max value, reset value and counter dependency).
And extracting event which depends on counter value.
This feature help you finding redundunt counter, deadlock loop, and other counter trouble. 

[Click here to know usage](https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/cnt_analyzer.md "cnt_analyzer")

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