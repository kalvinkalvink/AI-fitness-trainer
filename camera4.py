import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
import threading
import PoseModule as pm
from collections import deque

# Pose detector (heavy model load, keep global)
detector = pm.poseDetector(detectionCon=0.7, trackCon=0.7)  # Increased confidence thresholds

def open_camera():
    """Try indices 0-4, return an opened capture or None."""
    for idx in range(5):
        c = cv2.VideoCapture(idx)
        if c.isOpened():
            ok, _ = c.read()
            if ok:
                print(f"Camera opened at index {idx}")
                return c
            c.release()
    return None

# Lazily opened per exercise session (None until Start pressed)
cap = None
stop_event = threading.Event()
worker_thread = None

class ExerciseTracker:
    def __init__(self):
        self.angle_buffer = deque(maxlen=5)  # Smoothing buffer for angles
        self.prev_angles = {}  # Store previous angles for smoothing
        self.rep_threshold = 0.3  # Threshold for rep counting
        
    def smooth_angle(self, angle):
        """Apply smoothing to angle measurements"""
        self.angle_buffer.append(angle)
        return np.mean(self.angle_buffer)
    
    def calculate_bilateral_angles(self, img, lmlist, points):
        """Calculate angles for both left and right side with smoothing"""
        angles = {}
        for side in ['left', 'right']:
            p1, p2, p3 = points[side]
            try:
                angle = detector.finfAngle(img, p1, p2, p3)
                # Apply smoothing
                if f'{side}_angle' in self.prev_angles:
                    angle = 0.7 * angle + 0.3 * self.prev_angles[f'{side}_angle']
                self.prev_angles[f'{side}_angle'] = angle
                angles[side] = angle
            except:
                angles[side] = self.prev_angles.get(f'{side}_angle', 0)
        return angles

def exercise_logic(exercise_func, total_rep=10):
    count = 0
    dir = 0
    start_time = time.time()
    tracker = ExerciseTracker()
    fail_count = 0

    while count < total_rep and not stop_event.is_set():
        success, img = cap.read()
        if not success or img is None:
            fail_count += 1
            if fail_count > 30:
                print("Camera read failed 30x, stopping.")
                break
            time.sleep(0.01)
            continue
        fail_count = 0

        img = cv2.resize(img, (1288, 720))
        img = detector.findPose(img, False)
        lmlist = detector.findPosition(img, False)

        if len(lmlist) != 0:
            count, dir = exercise_func(img, lmlist, count, dir, tracker)

            cv2.putText(img, f'Reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            cv2.putText(img, f'Time: {int(time.time() - start_time)}s', (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Exercise Detection (press q to stop)", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyAllWindows()
    if cap is not None:
        cap.release()

def push_up_logic(img, lmlist, count, dir, tracker):
    # Points for both arms (shoulder, elbow, wrist)
    arm_points = {
        'left': (11, 13, 15),
        'right': (12, 14, 16)
    }
    
    # Calculate angles for both arms
    arm_angles = tracker.calculate_bilateral_angles(img, lmlist, arm_points)
    
    # Body alignment points (shoulder, hip, knee)
    body_points = {
        'left': (11, 23, 25),
        'right': (12, 24, 26)
    }
    body_angles = tracker.calculate_bilateral_angles(img, lmlist, body_points)
    
    # Calculate percentage for both arms
    left_per = np.interp(arm_angles['left'], (85, 165), (0, 100))
    right_per = np.interp(arm_angles['right'], (85, 165), (0, 100))
    
    # Check body alignment
    body_aligned = all(angle > 160 for angle in body_angles.values())
    
    # Average arm percentage for progress bar
    avg_per = (left_per + right_per) / 2
    
    # Count rep only if both arms are in correct position and body is aligned
    if avg_per > 95 and body_aligned and dir == 0:
        count += 0.5
        dir = 1
    if avg_per < 5 and body_aligned and dir == 1:
        count += 0.5
        dir = 0
        
    # Visual feedback
    progress_bar = np.interp(avg_per, (0, 100), (0, img.shape[1]))
    cv2.rectangle(img, (50, 50), (int(progress_bar), 100), (0, 255, 0), -1)
    
    # Form feedback
    if not body_aligned:
        cv2.putText(img, "Keep body straight!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    if abs(left_per - right_per) > 15:
        cv2.putText(img, "Keep arms even!", (50, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return count, dir

def squats_logic(img, lmlist, count, dir, tracker):
    # Points for both legs (hip, knee, ankle)
    leg_points = {
        'left': (23, 25, 27),
        'right': (24, 26, 28)
    }
    
    # Calculate angles for both legs
    leg_angles = tracker.calculate_bilateral_angles(img, lmlist, leg_points)
    
    # Hip points (shoulder, hip, knee)
    hip_points = {
        'left': (11, 23, 25),
        'right': (12, 24, 26)
    }
    hip_angles = tracker.calculate_bilateral_angles(img, lmlist, hip_points)
    
    # Calculate percentages
    left_per = np.interp(leg_angles['left'], (90, 170), (0, 100))
    right_per = np.interp(leg_angles['right'], (90, 170), (0, 100))
    avg_per = (left_per + right_per) / 2
    
    # Check proper form
    proper_depth = all(90 <= angle <= 110 for angle in leg_angles.values())
    proper_hip_hinge = all(angle >= 90 for angle in hip_angles.values())
    
    # Count rep
    if avg_per > 95 and dir == 0:
        count += 0.5
        dir = 1
    if proper_depth and proper_hip_hinge and dir == 1:
        count += 0.5
        dir = 0
    
    # Visual feedback
    progress_bar = np.interp(avg_per, (0, 100), (0, img.shape[1]))
    cv2.rectangle(img, (50, 50), (int(progress_bar), 100), (0, 255, 0), -1)
    
    # Form feedback
    if abs(left_per - right_per) > 15:
        cv2.putText(img, "Keep weight even!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    if not proper_hip_hinge:
        cv2.putText(img, "Hinge at hips!", (50, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return count, dir

def jumping_jacks_logic(img, lmlist, count, dir, tracker):
    # Points for arms and legs
    arm_points = {
        'left': (11, 13, 15),
        'right': (12, 14, 16)
    }
    leg_points = {
        'left': (23, 25, 27),
        'right': (24, 26, 28)
    }
    
    # Calculate angles
    arm_angles = tracker.calculate_bilateral_angles(img, lmlist, arm_points)
    leg_angles = tracker.calculate_bilateral_angles(img, lmlist, leg_points)
    
    # Calculate percentages
    arm_left_per = np.interp(arm_angles['left'], (30, 170), (0, 100))
    arm_right_per = np.interp(arm_angles['right'], (30, 170), (0, 100))
    leg_left_per = np.interp(leg_angles['left'], (10, 45), (0, 100))
    leg_right_per = np.interp(leg_angles['right'], (10, 45), (0, 100))
    
    avg_arm_per = (arm_left_per + arm_right_per) / 2
    avg_leg_per = (leg_left_per + leg_right_per) / 2
    
    # Count rep
    if avg_arm_per > 95 and avg_leg_per > 95 and dir == 0:
        count += 0.5
        dir = 1
    if avg_arm_per < 5 and avg_leg_per < 5 and dir == 1:
        count += 0.5
        dir = 0
    
    # Visual feedback
    progress_bar = np.interp(avg_arm_per, (0, 100), (0, img.shape[1]))
    cv2.rectangle(img, (50, 50), (int(progress_bar), 100), (0, 255, 0), -1)
    
    # Form feedback
    if abs(arm_left_per - arm_right_per) > 15:
        cv2.putText(img, "Keep arms even!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    if abs(leg_left_per - leg_right_per) > 15:
        cv2.putText(img, "Keep legs even!", (50, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return count, dir

def sit_up_logic(img, lmlist, count, dir, tracker):
    # Points for torso and legs
    torso_points = {
        'left': (11, 23, 25),
        'right': (12, 24, 26)
    }
    leg_points = {
        'left': (23, 25, 27),
        'right': (24, 26, 28)
    }
    
    # Calculate angles
    torso_angles = tracker.calculate_bilateral_angles(img, lmlist, torso_points)
    leg_angles = tracker.calculate_bilateral_angles(img, lmlist, leg_points)
    
    # Calculate percentage
    left_per = np.interp(torso_angles['left'], (70, 180), (0, 100))
    right_per = np.interp(torso_angles['right'], (70, 180), (0, 100))
    avg_per = (left_per + right_per) / 2
    
    # Check proper form
    proper_leg_position = all(40 <= angle <= 50 for angle in leg_angles.values())
    
    # Count rep
    if avg_per < 5 and proper_leg_position and dir == 0:
        count += 0.5
        dir = 1
    if avg_per > 95 and proper_leg_position and dir == 1:
        count += 0.5
        dir = 0
    
    # Visual feedback
    progress_bar = np.interp(avg_per, (0, 100), (0, img.shape[1]))
    cv2.rectangle(img, (50, 50), (int(progress_bar), 100), (0, 255, 0), -1)
    
    # Form feedback
    if not proper_leg_position:
        cv2.putText(img, "Keep legs at 45 degrees!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    if abs(left_per - right_per) > 15:
        cv2.putText(img, "Keep torso centered!", (50, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return count, dir

def lunges_logic(img, lmlist, count, dir, tracker):
    # Points for front and back legs
    leg_points = {
        'left': (23, 25, 27),
        'right': (24, 26, 28)
    }
    hip_points = {
        'left': (11, 23, 25),
        'right': (12, 24, 26)
    }
    
    # Calculate angles
    leg_angles = tracker.calculate_bilateral_angles(img, lmlist, leg_points)
    hip_angles = tracker.calculate_bilateral_angles(img, lmlist, hip_points)
    
    # Calculate percentage
    left_per = np.interp(leg_angles['left'], (85, 170), (0, 100))
    right_per = np.interp(leg_angles['right'], (85, 170), (0, 100))
    
    # Check proper form
    proper_front_knee = any(85 <= angle <= 95 for angle in leg_angles.values())
    proper_back_knee = any(85 <= angle <= 100 for angle in leg_angles.values())
    proper_torso = all(angle >= 160 for angle in hip_angles.values())
    
    # Count rep
    if proper_front_knee and proper_back_knee and proper_torso and dir == 0:
        count += 0.5
        dir = 1
    if all(per > 95 for per in [left_per, right_per]) and dir == 1:
        count += 0.5
        dir = 0
    
    # Visual feedback
    progress_bar = np.interp((left_per + right_per) / 2, (0, 100), (0, img.shape[1]))
    cv2.rectangle(img, (50, 50), (int(progress_bar), 100), (0, 255, 0), -1)
    
    # Form feedback
    if not proper_torso:
        cv2.putText(img, "Keep torso upright!", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    if not (proper_front_knee and proper_back_knee):
        cv2.putText(img, "Check knee angles!", (50, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return count, dir

# Create the GUI window
root = tk.Tk()
root.title("AI Fitness Trainer")
root.geometry("300x400")

# Style the window
root.configure(bg='#f0f0f0')
title_label = tk.Label(root, text="AI Fitness Trainer", font=("Arial", 18, "bold"), bg='#f0f0f0')
title_label.pack(pady=20)

# Exercise selection
exercise_var = tk.StringVar()
exercise_var.set("Push-ups")

exercises = {
    "Push-ups": push_up_logic,
    "Squats": squats_logic,
    "Jumping Jacks": jumping_jacks_logic,
    "Sit-ups": sit_up_logic,
    "Lunges": lunges_logic
}

# Create styled option menu
exercise_menu = tk.OptionMenu(root, exercise_var, *exercises.keys())
exercise_menu.configure(width=20)
exercise_menu.pack(pady=10)

# Function to start exercise
def run_session(exercise_fn):
    global cap
    cap = open_camera()
    if cap is None:
        root.after(0, lambda: messagebox.showerror(
            "Camera error",
            "Could not open any camera (tried indices 0-4).\n"
            "Check that /dev/video1 is accessible."))
        root.after(0, on_session_end)
        return
    exercise_logic(exercise_fn)
    root.after(0, on_session_end)

def on_session_end():
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    try:
        root.deiconify()
    except tk.TclError:
        pass

def start_exercise():
    global worker_thread
    if worker_thread is not None and worker_thread.is_alive():
        return
    stop_event.clear()
    selected_exercise = exercise_var.get()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    try:
        root.iconify()
    except tk.TclError:
        pass
    worker_thread = threading.Thread(
        target=run_session,
        args=(exercises[selected_exercise],),
        daemon=True)
    worker_thread.start()

def stop_exercise():
    stop_event.set()

# Create styled button
start_button = tk.Button(root, text="Start Exercise", 
                        command=start_exercise,
                        font=("Arial", 12),
                        bg='#4CAF50',
                        fg='white',
                        width=15,
                        height=2)
start_button.pack(pady=20)

# Add quit button
stop_button = tk.Button(root, text="Stop",
                       command=stop_exercise,
                       font=("Arial", 12),
                       bg='#FF9800',
                       fg='white',
                       width=15,
                       height=1,
                       state=tk.DISABLED)
stop_button.pack(pady=5)

quit_button = tk.Button(root, text="Quit",
                       command=root.quit,
                       font=("Arial", 12),
                       bg='#f44336',
                       fg='white',
                       width=15,
                       height=1)
quit_button.pack(pady=10)

def on_close():
    stop_event.set()
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Run the application
root.mainloop()

# Clean up
if cap is not None:
    try:
        cap.release()
    except Exception:
        pass
cv2.destroyAllWindows()