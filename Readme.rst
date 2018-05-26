|Build Status|

Introduction
============

Pyverilog\_toolbox is Pyverilog-based verification/design tool including
code clone finder, metrics calculator and so on. Pyverilog\_toolbox
accerating your digital circuit design verification. Thanks to Pyverilog
developer shtaxxx.

Software Requirements
=====================

-  Python (2.7 or 3.4)
-  Pyverilog (you can download from
   https://github.com/shtaxxx/Pyverilog) Pyverilog requires Icarus
   verilog

Installation
============

(If you want to use GUI stand alone version for windows, `Click here to
get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/gui.md>`__

If you want to use Pyverilog as a general library, you can install on
your environment by using setup.py.

::

    python setup.py install

Or you can use pip

::

    pip install pyverilog_toolbox

Features
========

codeclone\_finder
-----------------

codeclone\_finder can find pair of the register clone, which always hold
same value. Also can find pair of the invert register, which always hold
different value.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/codeclone.md>`__

combloop\_finder
----------------

Combinational logic loop is sticky problem, but you can find it by
combloop\_finder easily.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/combloop.md>`__

unreferenced\_finder
--------------------

Unreferenced\_finder can find signals which isn't referenced by any
signals. Also floating nodes can be found. By using this, you can delte
unnecessary codes.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/unreferenced.md>`__

metrics\_calculator
-------------------

metrics\_analyzer is metrics measurment tools for Verilog HDL. You can
visualize complecity of module/register/function/.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/metrics.md>`__

regmap\_analyzer
----------------

regmap\_analyzer can analyze register map structure from RTL.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/regmap.md>`__

cnt\_analyzer
-------------

cnt\_analyzer analyze counter property(up or down, max value, reset
value and counter dependency). And extracting event which depends on
counter value. This feature help you finding redundunt counter, deadlock
loop, and other counter trouble.

`Click here to get
detail <https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/cnt_analyzer.md>`__

License
=======

Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

Copyright
=========

Copyright (C) 2015, Ryosuke Fukatani

Related Project and Site
========================

Pyverilog https://github.com/shtaxxx/Pyverilog

Blog entry(in Japanese)
http://segafreder.hatenablog.com/entry/2015/05/23/161000

.. |Build Status| image:: https://travis-ci.org/fukatani/Pyverilog_toolbox.svg?branch=master
   :target: https://travis-ci.org/fukatani/Pyverilog_toolbox
