# -*- mode: python -*-
a = Analysis(['.\\gui_main.py'],
             pathex=['C:\\Users\\rf\\Documents\\github\\pyverilog_toolbox\\pyverilog_toolbox\\gui',
	            'C:\\Users\\rf\\Documents\\github\\pyverilog_toolbox',
#                    'C:\\Python27\\Lib\\site-packages\\wx-3.0-msw\\wx',
                    'C:\\Python27\\Lib\\site-packages',
                    'C:\\Python27\\Lib\\site-packages\\pyverilog'],
             hiddenimports=['pyverilog_toolbox',
                           'pyverilog_toolbox.verify_tool.regmap_analyzer',
                           'pyverilog',
                           'pyverilog.dataflow_analyzer'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='gui_main.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='pyv_gui')
