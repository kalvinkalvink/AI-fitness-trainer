import cv2
import numpy as np

NAME = "Lunges"


def logic(img, lmlist, count, dir, tracker):
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
