import wx
import wx.html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from pyverilog_toolbox.verify_tool.regmap_analyzer import *
from pyverilog_toolbox.verify_tool.combloop_finder import *
from pyverilog_toolbox.verify_tool.bindlibrary import *
from pyverilog_toolbox.verify_tool.cnt_analyzer import *
from pyverilog_toolbox.verify_tool.codeclone_finder import CodeCloneFinder
from pyverilog_toolbox.verify_tool.unreferenced_finder import UnreferencedFinder
from pyverilog_toolbox.verify_tool.metrics_calculator import MetricsCalculator

class OutputDisplay(wx.Frame):
    debug = False
    def __init__(self, log_file_name):

        wx.Frame.__init__(self,None,wx.ID_ANY,"Output",size=(900,700))
        log = open(log_file_name, 'r')
        log_disp_panel = wx.html.HtmlWindow(self)
        if "gtk2" in wx.PlatformInfo:
            log_disp_panel.SetStandardFonts()
        log_disp_panel.SetPage("".join(log.readlines()))

if __name__ == "__main__":
    application = wx.App()
    frame = OutputDisplay("log.html")
    frame.Show()
    application.MainLoop()