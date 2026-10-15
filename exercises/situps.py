import cv2
import numpy as np

NAME = "Sit-ups"


def logic(img, lmlist, count, dir, tracker):
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
