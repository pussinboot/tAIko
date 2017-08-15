import win32api
import win32con
import win32gui

import time
import random
import os

# assumptions
# rom is loaded up already
# save state 1 is main menu (you have to create an acct etc)

EMU_TITLES = ['DeSmuME', 'Paused']
SCROT_PATH = 'c:/games/emu/desmume-0.9.11-win64/Screenshots/'

# ctrl+f12 = scrot


class KeyPresser:
    def __init__(self, quit_fun=None):
        self.last_hwnd = None
        self.paused = None

        self.key_delay = 0.175
        self.key_map = {
            'up': 0x26,
            'down': 0x28,
            'left': 0x25,
            'right': 0x27,
            "a": ord("X"),
            "b": ord("Z"),
            "l": ord("S"),
            "r": ord("A"),
            "start": 0x0D,
            'pause': 0x13,
            'step': ord("N"),
            'ctrl': 0x11,
            'alt': 0xA4,
            'F1': 0x70,
            '[': 0xDB,
            'F12': 0x7B,
        }

        self.quit_fun = quit_fun

    def _window_enum_callback(self, hwnd, *args):
        win_title = str(win32gui.GetWindowText(hwnd))
        if any(title in win_title for title in EMU_TITLES):
            self.last_hwnd = hwnd
            self.paused = EMU_TITLES[1] in win_title

    def activate_emulator(self):
        win32gui.EnumWindows(self._window_enum_callback, None)
        if self.last_hwnd is not None:
            try:
                win32gui.SetForegroundWindow(self.last_hwnd)
                return True
            except:
                if self.quit_fun is not None:
                    self.quit_fun()
                return False
        return False

    def send_keys(self, buts, rev=True):
        cur_hwnd = win32gui.GetForegroundWindow()
        if cur_hwnd != self.last_hwnd:
            if not self.activate_emulator():
                print('failed to find your emulator')
                return
            time.sleep(0.125)
        for but in buts:
            win32api.keybd_event(self.key_map[but], 0, 0, 0)
            time.sleep(self.key_delay)

        if rev:
            buts.reverse()

        for but in buts:
            win32api.keybd_event(self.key_map[but], 0, win32con.KEYEVENTF_KEYUP, 0)

    def send_key(self, but):
        self.send_keys([but])

    def send_keys_combo(self, buts):
        self.send_keys(buts, False)

    def unpause(self):
        if self.paused is None:
            # find out if paused
            if not self.activate_emulator():
                print('failed to find your emulator')
                return
            self.unpause()
            return
        if self.paused:
            self.send_key('pause')


class GamePlayer:
    def __init__(self, kpq):
        self.kp = KeyPresser(kpq)
        self.cc_to_but = {'o': ['a', 'b'], 'b': ['l', 'r']}

    def back_to_menu(self):
        self.kp.unpause()
        time.sleep(0.1)
        self.kp.send_key('F1')

    def get_action_keys(self, color, count=0):
        if color in self.cc_to_but:
            return self.cc_to_but[color][:count]


class Training(GamePlayer):
    def __init__(self, kpq=None):
        GamePlayer.__init__(self, kpq)

    def choose_new_track(self):
        self.back_to_menu()
        # 28 total tracks to choose from..
        steps = random.randint(0, 27)
        for _ in range(steps):
            self.kp.send_key('left')
            time.sleep(0.2)
        self.kp.send_key('a')
        time.sleep(3.5)
        self.kp.send_key('pause')

    def advance_frame(self, any_action=None):
        time.sleep(0.125)
        to_press = []
        if any_action is not None:
            ak = self.get_action_keys(*any_action)
            if ak is not None:
                to_press = ak
        to_press += ['step']
        self.kp.send_keys(to_press)

        # screenshot
        self.kp.send_keys_combo(['ctrl', 'F12'])

    def find_last_frame(self):
        all_frames = os.listdir(SCROT_PATH)
        f_paths = [os.path.join(SCROT_PATH, f) for f in all_frames]
        return max(f_paths, key=os.path.getctime)


if __name__ == '__main__':
    trainer = Training()
    # trainer.kp.send_key('pause')

    trainer.choose_new_track()
    # for _ in range(5):
    #     trainer.advance_frame()

    # trainer.advance_frame(['o', 1])

    # for _ in range(3):
    #     trainer.advance_frame()

    # print(trainer.find_last_frame())
