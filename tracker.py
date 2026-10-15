import numpy as np
from collections import deque


class ExerciseTracker:
    def __init__(self, detector):
        self.detector = detector
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
                angle = self.detector.finfAngle(img, p1, p2, p3)
                # Apply smoothing
                if f'{side}_angle' in self.prev_angles:
                    angle = 0.7 * angle + 0.3 * self.prev_angles[f'{side}_angle']
                self.prev_angles[f'{side}_angle'] = angle
                angles[side] = angle
            except:
                angles[side] = self.prev_angles.get(f'{side}_angle', 0)
        return angles
