import cv2
import numpy as np

NAME = "Push-ups"


def logic(img, lmlist, count, dir, tracker):
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
