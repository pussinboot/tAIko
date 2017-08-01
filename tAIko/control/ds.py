import win32api
import win32con
import win32gui

import time

EMU_TITLES = ['DeSmuME', 'Paused']

# ctrl+f12 = scrot

class KeyPresser:
    def __init__(self):
        self.last_hwnd = None

        self.key_delay = 0.15
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
            'F12': 0x7B,
        }

    def _window_enum_callback(self, hwnd, *args):
        if any(title in str(win32gui.GetWindowText(hwnd)) for title in EMU_TITLES):
            self.last_hwnd = hwnd

    def activate_emulator(self):
        win32gui.EnumWindows(self._window_enum_callback, None)
        if self.last_hwnd is not None:
            win32gui.SetForegroundWindow(self.last_hwnd)
            return True
        return False

    def send_keys(self, buts, rev=True):
        cur_hwnd = win32gui.GetForegroundWindow()
        if cur_hwnd != self.last_hwnd:
            if not self.activate_emulator():
                print('failed to find your emulator')
                return

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

# training class
# - needs to do presses (1 or 2, o or b)
# - needs to advance frames & take screenshots (& tell us how to find latest screenshot)

if __name__ == '__main__':
    kp = KeyPresser()
    # kp.send_key('start')
    # time.sleep(0.5)b
    kp.send_keys(['a', 'step'])
    kp.send_keys_combo(['ctrl', 'F12'])

    # time.sleep(0.5)
    # kp.send_key('start')
