<p>[![Build Status](<a href="https://travis-ci.org/fukatani/Pyverilog_toolbox.svg?branch=master" class="uri">https://travis-ci.org/fukatani/Pyverilog_toolbox.svg?branch=master</a>)](<a href="https://travis-ci.org/fukatani/Pyverilog_toolbox" class="uri">https://travis-ci.org/fukatani/Pyverilog_toolbox</a>)</p>
<h1 id="introduction">Introduction</h1>
<p>Pyverilog_toolbox is Pyverilog-based verification/design tool including code clone finder, metrics calculator and so on. Pyverilog_toolbox accerating your digital circuit design verification. Thanks to Pyverilog developer shtaxxx.</p>
<h1 id="software-requirements">Software Requirements</h1>
<ul>
<li>Python (2.7 or 3.4)</li>
</ul>
<p>* Pyverilog (you can download from <a href="https://github.com/shtaxxx/Pyverilog" class="uri">https://github.com/shtaxxx/Pyverilog</a>) Pyverilog requires Icarus verilog</p>
<h1 id="installation">Installation</h1>
<p>(If you want to use GUI stand alone version for windows, [Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/gui.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/gui.md</a>)</p>
<p>If you want to use Pyverilog as a general library, you can install on your environment by using setup.py.</p>
<p><code>` python setup.py install</code>`</p>
<p>Or you can use pip <code>` pip install pyverilog_toolbox</code>`</p>
<h1 id="features">Features</h1>
<p>## codeclone_finder codeclone_finder can find pair of the register clone, which always hold same value. Also can find pair of the invert register, which always hold different value.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/codeclone.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/codeclone.md</a> &quot;codeclone_finder&quot;)</p>
<p>## combloop_finder</p>
<p>Combinational logic loop is sticky problem, but you can find it by combloop_finder easily.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/combloop.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/combloop.md</a> &quot;combloop_finder&quot;)</p>
<p>## unreferenced_finder</p>
<p>Unreferenced_finder can find signals which isn't referenced by any signals. Also floating nodes can be found. By using this, you can delte unnecessary codes.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/unreferenced.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/unreferenced.md</a> &quot;unreferenced_finder&quot;)</p>
<p>##metrics_calculator</p>
<p>metrics_analyzer is metrics measurment tools for Verilog HDL. You can visualize complecity of module/register/function/.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/metrics.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/metrics.md</a> &quot;metrics_analyzer&quot;)</p>
<p>## regmap_analyzer</p>
<p>regmap_analyzer can analyze register map structure from RTL.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/regmap.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/regmap.md</a> &quot;regmap_analyzer&quot;)</p>
<p>## cnt_analyzer</p>
<p>cnt_analyzer analyze counter property(up or down, max value, reset value and counter dependency). And extracting event which depends on counter value. This feature help you finding redundunt counter, deadlock loop, and other counter trouble.</p>
<p>[Click here to get detail](<a href="https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/cnt_analyzer.md" class="uri">https://github.com/fukatani/Pyverilog_toolbox/blob/master/pyverilog_toolbox/docs/cnt_analyzer.md</a> &quot;cnt_analyzer&quot;)</p>
<h1 id="license">License</h1>
<p>Apache License 2.0 (<a href="http://www.apache.org/licenses/LICENSE-2.0" class="uri">http://www.apache.org/licenses/LICENSE-2.0</a>)</p>
<h1 id="copyright">Copyright</h1>
<p>Copyright (C) 2015, Ryosuke Fukatani</p>
<h1 id="related-project-and-site">Related Project and Site</h1>
<p>Pyverilog <a href="https://github.com/shtaxxx/Pyverilog" class="uri">https://github.com/shtaxxx/Pyverilog</a></p>
<p>Blog entry(in Japanese) <a href="http://segafreder.hatenablog.com/entry/2015/05/23/161000" class="uri">http://segafreder.hatenablog.com/entry/2015/05/23/161000</a></p>
