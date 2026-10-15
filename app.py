import cv2
import threading
import tkinter as tk
from tkinter import messagebox

from camera import open_camera
from exercises import EXERCISES
from pose_detector import PoseDetector
from session import run_session


class ExerciseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.detector = PoseDetector(detectionCon=0.7, trackCon=0.7)
        self.cap = None
        self.stop_event = threading.Event()
        self.worker = None

        self.title("AI Fitness Trainer")
        self.geometry("300x400")
        self.configure(bg='#f0f0f0')

        self.title_label = tk.Label(self, text="AI Fitness Trainer", font=("Arial", 18, "bold"), bg='#f0f0f0')
        self.title_label.pack(pady=20)

        self.exercise_var = tk.StringVar()
        self.exercise_var.set("Push-ups")

        self.exercise_menu = tk.OptionMenu(self, self.exercise_var, *EXERCISES.keys())
        self.exercise_menu.configure(width=20)
        self.exercise_menu.pack(pady=10)

        self.start_button = tk.Button(self, text="Start Exercise",
                                      command=self.start_exercise,
                                      font=("Arial", 12),
                                      bg='#4CAF50',
                                      fg='white',
                                      width=15,
                                      height=2)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(self, text="Stop",
                                     command=self.stop_exercise,
                                     font=("Arial", 12),
                                     bg='#FF9800',
                                     fg='white',
                                     width=15,
                                     height=1,
                                     state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.quit_button = tk.Button(self, text="Quit",
                                     command=self.quit,
                                     font=("Arial", 12),
                                     bg='#f44336',
                                     fg='white',
                                     width=15,
                                     height=1)
        self.quit_button.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_exercise(self):
        if self.worker is not None and self.worker.is_alive():
            return
        self.stop_event.clear()
        selected_exercise = self.exercise_var.get()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        try:
            self.iconify()
        except tk.TclError:
            pass
        self.worker = threading.Thread(
            target=self._run_session,
            args=(selected_exercise,),
            daemon=True)
        self.worker.start()

    def _run_session(self, name):
        self.cap = open_camera()
        if self.cap is None:
            self.after(0, lambda: messagebox.showerror(
                "Camera error",
                "Could not open any camera (tried indices 0-4).\n"
                "Check that /dev/video1 is accessible."))
            self.after(0, self.on_session_end)
            return
        run_session(self.cap, self.detector, EXERCISES[name], self.stop_event)
        self.after(0, self.on_session_end)

    def on_session_end(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        try:
            self.deiconify()
        except tk.TclError:
            pass

    def stop_exercise(self):
        self.stop_event.set()

    def on_close(self):
        self.stop_event.set()
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        cv2.destroyAllWindows()
        self.destroy()


def main():
    app = ExerciseApp()
    app.mainloop()
