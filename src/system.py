import sys
import winreg

def is_frozen_app():
    return getattr(sys, 'frozen', False)


def set_autostart(value):
    # determine if application is a script file or frozen exe
    #if is_frozen_app():
    if value:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                             winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'Analytics Assist', 0,
                          winreg.REG_SZ, sys.executable)  # file_path is path of file after coping it

        winreg.CloseKey(key)
    else:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                             winreg.KEY_WRITE)
        winreg.DeleteValue(key, 'Analytics Assist')
        winreg.CloseKey(key)

def get_autostart():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0)
    try:
        value = winreg.QueryValueEx(key, 'Analytics Assist')[0] == sys.executable
    except FileNotFoundError:
        value = False
    winreg.CloseKey(key)
    return value