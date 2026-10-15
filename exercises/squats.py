import cv2
import numpy as np

NAME = "Squats"


def logic(img, lmlist, count, dir, tracker):
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
