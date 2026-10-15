import cv2
import numpy as np

NAME = "Jumping Jacks"


def logic(img, lmlist, count, dir, tracker):
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
