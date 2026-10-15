import cv2


def open_camera(indices=range(5)):
    """Try indices 0-4, return an opened capture or None."""
    for idx in indices:
        c = cv2.VideoCapture(idx)
        if c.isOpened():
            ok, _ = c.read()
            if ok:
                print(f"Camera opened at index {idx}")
                return c
            c.release()
    return None
