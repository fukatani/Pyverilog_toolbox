import wx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

from pyverilog.utils.verror import *
from pyverilog_toolbox.verify_tool.regmap_analyzer import *
from pyverilog_toolbox.verify_tool.combloop_finder import *
from pyverilog_toolbox.verify_tool.bindlibrary import *
from pyverilog_toolbox.verify_tool.cnt_analyzer import *
from pyverilog_toolbox.verify_tool.codeclone_finder import CodeCloneFinder
from pyverilog_toolbox.verify_tool.unreferenced_finder import UnreferencedFinder
from pyverilog_toolbox.verify_tool.metrics_calculator import MetricsCalculator
from pyverilog_toolbox.verify_tool.combloop_finder import CombLoopFinder
from pyverilog_toolbox.verify_tool.bindlibrary import CombLoopException
from pyverilog_toolbox.verify_tool.cnt_analyzer import CntAnalyzer

from pyverilog_toolbox.gui.output_display import OutputDisplay

class GuiMain(wx.Frame):
    debug = False
    def __init__(self):

        wx.Frame.__init__(self,None,wx.ID_ANY,"Pyv_guitools",size=(450,550))

        # initialiuze status bar
        self.CreateStatusBar()
        self.SetStatusText("")
        self.GetStatusBar().SetBackgroundColour(None)

        # initialiuze menu bar
        self.SetMenuBar(Menu())

        # build body
        self.commands = ("dataflow analyzer", "controlflow analyzer", "calc metrics",
                         "find combinational loop", "find unused variables", "find code clone", "analyze counter")
        root_panel = wx.Panel(self,wx.ID_ANY)
        root_layout = wx.BoxSizer(wx.VERTICAL)

        self.top_name_panel       = TextPanel(root_panel)
        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "TOP MODULE NAME:"), border=5)
        root_layout.Add(self.top_name_panel, 0, wx.GROW|wx.ALL, border=5)

        filebutton_panel = CommandButtonPanel(root_panel, "Verilog file select", self.click_fs_button)
        self.selected_file_panel = wx.StaticText(root_panel, wx.ID_ANY, "")
        root_layout.Add(filebutton_panel, 0, wx.GROW|wx.ALL,border=5)
        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "Selecting verilog file:"), border=5)
        root_layout.Add(self.selected_file_panel, border=5)

        self.radiobutton_panel = RadioPanel(root_panel, self.commands)
        root_layout.Add(self.radiobutton_panel, 0, wx.GROW|wx.ALL, border=10)

        exebutton_panel  = CommandButtonPanel(root_panel, "EXECUTE!", self.click_exe_button)
        root_layout.Add(exebutton_panel, 0, wx.GROW|wx.LEFT|wx.RIGHT, border=5)

        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

    def click_fs_button(self, event):
        frame.SetStatusText("Selecting verilog file(s)...")
        self.dirname = ''

        f_dlg = wx.FileDialog(self, "Select verilog file(s)", self.dirname, "", "*.*", wx.FD_MULTIPLE)
        if f_dlg.ShowModal() == wx.ID_OK:
            self.selected_vfiles = f_dlg.GetFilenames()
            self.selected_full_path = [f_dlg.GetDirectory() + "\\" + vfile for vfile in self.selected_vfiles]
            if len(self.selected_vfiles) > 1:
                self.selected_file_panel.SetLabel(self.selected_vfiles[0] + ', ...')
            else:
                self.selected_file_panel.SetLabel(self.selected_vfiles[0])

        self.SetStatusText("")
        f_dlg.Destroy()

    def click_exe_button(self, event):
        now_command = self.radiobutton_panel.get_selected_item()
        if self.debug:
            print(now_command)

        if not hasattr(self, 'selected_vfiles'):
            self.ShowErrorMessage('Please select verilog files before execution.')
            return

        log_file_name = 'log.html'
        try:
            if now_command == 'dataflow analyzer':
                df = dataflow_facade(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                df.html_name = log_file_name
                df.print_dataflow()
            elif now_command == 'controlflow analyzer':
                df = dataflow_facade(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                df.html_name = log_file_name
                df.print_controlflow()
            elif now_command == 'calc metrics':
                mc = MetricsCalculator(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                mc.html_name = log_file_name
                mc.synth_profile()
                mc.show()
            elif now_command == 'find combinational loop':
                cf = CombLoopFinder(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                cf.html_name = log_file_name
                cf.search_combloop()
            elif now_command == 'find unused variables':
                uf = UnreferencedFinder(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                uf.html_name = log_file_name
                uf.search_unreferenced()
            elif now_command == 'find code clone':
                cf = CodeCloneFinder(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                cf.html_name = log_file_name
                cf.show()
            elif now_command == 'analyze counter':
                ca = CntAnalyzer(self.selected_full_path, topmodule=self.top_name_panel.get_text())
                ca.html_name = log_file_name
                ca.show()
            else:
                self.ShowErrorMessage('unimplemented function')
                return
            OutputDisplay(log_file_name).Show()
        except (DefinitionError, FormatError, ImplementationError, CombLoopException) as e:
            self.ShowErrorMessage(e.message)

    def ShowErrorMessage(self, message):
        wx.MessageBox(message, 'Error!', wx.ICON_ERROR)

class Menu(wx.MenuBar):

    def __init__(self):

        wx.MenuBar.__init__(self)

        menu_menu = wx.Menu()
        menu_menu.Append(wx.ID_ANY,"Usage(visit gitbub page online)")
        menu_menu.Append(wx.ID_ANY,"quit")
        self.Append(menu_menu,"menu")

##        menu_edit = wx.Menu()
##        menu_edit.Append(wx.ID_ANY,"copy")
##        menu_edit.Append(wx.ID_ANY,"paste")
##        self.Append(menu_edit,"edit")

class TextPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self,parent, wx.ID_ANY)
        self.disp_text = wx.TextCtrl(self, wx.ID_ANY, "TOP", style=wx.TE_RIGHT)
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(self.disp_text, 1)
        self.SetSizer(layout)
    def get_text(self):
        return self.disp_text.GetValue()

class CommandButtonPanel(wx.Panel):

    def __init__(self, parent, disp_text, click_event):

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        button = wx.Button(self, wx.ID_ANY, disp_text)
        button.Bind(wx.EVT_BUTTON, click_event)
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(button,flag=wx.GROW)
        self.SetSizer(layout)

class RadioPanel(wx.Panel):
    def __init__(self, parent, button_array):
        wx.Panel.__init__(self,parent,wx.ID_ANY)

        self.radiobox = wx.RadioBox(self, wx.ID_ANY, choices=button_array, style=wx.RA_VERTICAL)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.radiobox, 1, flag=wx.GROW)

        self.SetSizer(layout)

    def get_selected_item(self):
        return self.radiobox.GetStringSelection()


if __name__ == "__main__":
    application = wx.App(redirect=True)
    frame = GuiMain()
    frame.Show()
    application.MainLoop()