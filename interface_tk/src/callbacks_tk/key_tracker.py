import threading
import time

class KeyTracker():
    def __init__(self):
        self.track("space")
    
    key = ''
    last_press_time = 0
    last_release_time = 0

    def track(self, key):
        self.key = key
        print(key)

    def is_pressed(self):
        return time.time() - self.last_press_time < .1

    def report_key_press(self, event):
        if event.keysym == self.key:
            print("key_pressionated", event.keysym)
            self.last_press_time = time.time()

    def report_key_release(self, event):
        if event.keysym == self.key:
            timer = threading.Timer(.1, self.report_key_release_callback, args=[event])
            timer.start()

    def report_key_release_callback(self, event):
        if not self.is_pressed():
            print("Not")
        self.last_release_time = time.time()