import wx
import wx.html
import os
import sys
import webbrowser
import warnings
import wx.lib.agw.persist as PM

if getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))))
elif __file__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

#from pyverilog_toolbox.gui.output_display import OutputDisplay

class GuiMain(wx.Frame):
    debug = False

    def OnClose(self, event):
        self._persistMgr.SaveAndUnregister()
        self.vfile_data.dump()
        event.Skip()

    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY,"Pyv_guitools",size=(450,550))

        # initialiuze status bar
        self.CreateStatusBar()
        self.SetStatusText("")
        self.GetStatusBar().SetBackgroundColour(None)

        # initialiuze menu bar
        self.Bind(wx.EVT_MENU, self.selectMenu)
        self.SetMenuBar(Menu())

        # build body
        self.commands = ("exec dataflow analyzer", "exec controlflow analyzer", "calculate code metrics",
                         "find combinational loop", "find unused variables", "find code clone",
                         "analyze counter", "analyze register map")
        root_panel = wx.Panel(self,wx.ID_ANY)
        root_layout = wx.BoxSizer(wx.VERTICAL)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "TOP MODULE NAME:"), border=5)
        self.top_name_panel = TextPanel(root_panel)
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

        self.dirname = ''

        #for persistence
        self.SetName('gui_main.dump')
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._persistMgr = PM.PersistenceManager.Get()
        wx.CallAfter(self.RegisterControls)
        self.vfile_data = self.f_data()

    def RegisterControls(self):
        self.Freeze()
        self.Register()
        self.Thaw()

    def Register(self, children=None):
        if children is None:
            self._persistMgr.RegisterAndRestore(self)
            children = self.GetChildren()

        for child in children:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                name = child.GetName()
            if name not in PM.BAD_DEFAULT_NAMES and 'widget' not in name and \
               'wxSpinButton' not in name:
                self._persistMgr.RegisterAndRestore(child)
            if child.GetChildren():
                self.Register(child.GetChildren())

    def click_fs_button(self, event):
        f_dlg = wx.FileDialog(self, "Select verilog file(s)", self.dirname, "", "*.*", wx.FD_MULTIPLE)
        self.SetStatusText("Selecting verilog file(s)...")
        if f_dlg.ShowModal() == wx.ID_OK:
            self.vfile_data.set_files(f_dlg.GetFilenames(), f_dlg.GetDirectory(), self.selected_file_panel)
        self.SetStatusText("")
        f_dlg.Destroy()

    def selectMenu(self, event):
        if event.GetId() == wx.ID_ABOUT:
            webbrowser.open('https://github.com/fukatani/Pyverilog_toolbox/blob/master/Readme.md')
        elif event.GetId() == wx.ID_EXIT:
            self.Destroy()

    def click_exe_button(self, event):
        now_command = self.radiobutton_panel.get_selected_item()
        if self.debug:
            print(now_command)

        if not hasattr(self.vfile_data, 'selected_vfiles'):
            self.ShowErrorMessage('Please select verilog files before execution.')
            return

        log_file_name = 'log.html'

        self.SetStatusText("Analyzing...")
        try:
            if now_command == 'exec dataflow analyzer':
                df = dataflow_facade(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                df.html_name = log_file_name
                df.print_dataflow()
            elif now_command == 'exec controlflow analyzer':
                df = dataflow_facade(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                df.html_name = log_file_name
                df.print_controlflow()
            elif now_command == 'calculate code metrics':
                mc = MetricsCalculator(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                mc.html_name = log_file_name
                mc.synth_profile()
                mc.show()
            elif now_command == 'find combinational loop':
                cf = CombLoopFinder(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                cf.html_name = log_file_name
                cf.search_combloop()
            elif now_command == 'find unused variables':
                uf = UnreferencedFinder(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                uf.html_name = log_file_name
                uf.search_unreferenced()
            elif now_command == 'find code clone':
                cf = CodeCloneFinder(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                cf.html_name = log_file_name
                cf.show()
            elif now_command == 'analyze counter':
                ca = CntAnalyzer(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text())
                ca.html_name = log_file_name
                ca.show()
            elif now_command == "analyze register map":
                RegMapConfig(self.vfile_data.selected_full_path, topmodule=self.top_name_panel.get_text()).Show()
                return
            else:
                self.ShowErrorMessage('unimplemented function')
                return
            OutputDisplay(log_file_name).Show()
            self.SetStatusText("")
        except (DefinitionError, FormatError, ImplementationError, CombLoopException) as e:
            self.ShowErrorMessage(e.message)
        except IOError as e:
            if e.filename == 'preprocess.output':
                self.ShowErrorMessage(e.filename + 'is not found.' + '\n(Please make sure Icarus verilog is installed)')
            else:
                self.ShowErrorMessage(e.filename + 'is not found.')
    def ShowErrorMessage(self, message):
        wx.MessageBox(message, 'Error!', wx.ICON_ERROR)

    class f_data(object):
        """ [CLASSES]
        Selected verilog file data.
        Registerd by pickle.
        """
        def __init__(self):
            self.dump_enable = False
            if self.dump_enable:
                try:
                    with open("pyv.dump", "r") as f:
                        (self.selected_vfiles, self.selected_full_path) = pickle.load(f)
                    #if hasattr(self, 'selected_full_path'):
                except (IOError, EOFError):
                    pass


        def __get_state__(self):
            return self.selected_vfiles, self.selected_full_path

        def set_label(self, file_panel):
            if len(self.selected_vfiles) > 1:
                file_panel.SetLabel(self.selected_vfiles[0] + ', ...')
            else:
                file_panel.SetLabel(self.selected_vfiles[0])

        def set_files(self, filenames, directory, file_panel):
            self.selected_vfiles = filenames
            self.selected_full_path = [directory + "\\" + vfile for vfile in self.selected_vfiles]
            self.set_label(file_panel)

        def dump(self):
            if self.dump_enable:
                with open("pyv.dump", "w") as f:
                    pickle.dump(self, f)

class Menu(wx.MenuBar):

    def __init__(self):

        wx.MenuBar.__init__(self)

        menu_menu = wx.Menu()
        menu_menu.Append(wx.ID_ABOUT,"display usage(visit online github page)","https://github.com/fukatani/Pyverilog_toolbox")
        menu_menu.Append(wx.ID_EXIT,"exit","exit pyv_gui")
        self.Append(menu_menu,"menu")

class TextPanel(wx.Panel):

    def __init__(self, parent, initial="TOP"):
        wx.Panel.__init__(self,parent, wx.ID_ANY)
        self.disp_text = wx.TextCtrl(self, wx.ID_ANY, initial, style=wx.TE_RIGHT)
        self.disp_text.SetName(initial + ".dump")
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
        self.radiobox.SetName("command_select.dump")
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.radiobox, 1, flag=wx.GROW)

        self.SetSizer(layout)

    def get_selected_item(self):
        return self.radiobox.GetStringSelection()

class RegMapConfig(wx.Frame):
    def __init__(self, full_path, topmodule):
        wx.Frame.__init__(self,None,wx.ID_ANY,"Analyze register map",size=(300,400))
        self.full_path = full_path
        self.topmodule = topmodule
        self.__persistMgr = PM.PersistenceManager.Get()

        root_panel = wx.Panel(self,wx.ID_ANY)
        root_layout = wx.BoxSizer(wx.VERTICAL)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "WRITE FLAG SIGNAL:"), border=5)
        self.write_flag_panel = TextPanel(root_panel, "TOP.WRITE")
        root_layout.Add(self.write_flag_panel, 0, wx.GROW|wx.ALL, border=5)

##        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "READ FLAG SIGNAL:"), border=5)
##        self.read_flag_panel = TextPanel(root_panel, "TOP.READ")
##        root_layout.Add(self.read_flag_panel, 0, wx.GROW|wx.ALL, border=5)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "ADDRESS SIGNAL"), border=5)
        self.address_panel = TextPanel(root_panel, "TOP.ADR")
        root_layout.Add(self.address_panel, 0, wx.GROW|wx.ALL, border=5)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "WRITE DATA SIGNAL"), border=5)
        self.write_data_panel = TextPanel(root_panel, "TOP.W_DATA")
        root_layout.Add(self.write_data_panel, 0, wx.GROW|wx.ALL, border=5)

        root_layout.Add(wx.StaticText(root_panel, wx.ID_ANY, "READ DATA SIGNAL"), border=5)
        self.read_data_panel = TextPanel(root_panel, "TOP.R_DATA")
        root_layout.Add(self.read_data_panel, 0, wx.GROW|wx.ALL, border=5)

        exebutton_panel  = CommandButtonPanel(root_panel, "EXECUTE!", self.click_exe_button)
        root_layout.Add(exebutton_panel, 0, wx.GROW|wx.LEFT|wx.RIGHT, border=5)

        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

        #for persistence
        self.SetName('regmap_config.dump')
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self._persistMgr = PM.PersistenceManager.Get()
        wx.CallAfter(self.RegisterControls)

    def click_exe_button(self, event):
        with open("setup.txt", "w") as setup_file:
            setup_file.write("READ_FLAG:" + "None" + "\n")
            setup_file.write("WRITE_FLAG:" + self.write_flag_panel.get_text() + "\n")
            setup_file.write("ADDRESS:" + self.address_panel.get_text() + "\n")
            setup_file.write("WRITE_DATA:" + self.write_data_panel.get_text() + "\n")
            setup_file.write("READ_DATA:" + self.read_data_panel.get_text() + "\n")
        ra = RegMapAnalyzer(self.full_path, "setup.txt", self.topmodule, "out.csv")
        ra.getRegMaps()
        ra.csv2html("out.csv")
        OutputDisplay("log.html").Show()

    def RegisterControls(self):
        self.Freeze()
        self.Register()
        self.Thaw()

    def Register(self, children=None):
        if children is None:
            self._persistMgr.RegisterAndRestore(self)
            children = self.GetChildren()

        for child in children:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                name = child.GetName()
            if name not in PM.BAD_DEFAULT_NAMES and 'widget' not in name and \
               'wxSpinButton' not in name:
                self._persistMgr.RegisterAndRestore(child)
            if child.GetChildren():
                self.Register(child.GetChildren())

    def OnClose(self, event):
        self._persistMgr.SaveAndUnregister()
        event.Skip()

class OutputDisplay(wx.Frame):
    def __init__(self, log_file_name):
        wx.Frame.__init__(self,None,wx.ID_ANY,"Output report",size=(900,700))
        log = open(log_file_name, 'r')
        log_disp_panel = wx.html.HtmlWindow(self)
        if "gtk2" in wx.PlatformInfo:
            log_disp_panel.SetStandardFonts()
        log_disp_panel.SetPage("".join(log.readlines()))


if __name__ == "__main__":
    build_flag = False
    application = wx.App(redirect=build_flag)#false in debugging
    frame = GuiMain()
    frame.Show()
    application.MainLoop()


