import cv2
import numpy as np
import time

from tracker import ExerciseTracker


def run_session(cap, detector, exercise_fn, stop_event, total_rep=10):
    tracker = ExerciseTracker(detector)
    count = 0
    dir = 0
    start_time = time.time()
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
            count, dir = exercise_fn(img, lmlist, count, dir, tracker)

            cv2.putText(img, f'Reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            cv2.putText(img, f'Time: {int(time.time() - start_time)}s', (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Exercise Detection (press q to stop)", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cv2.destroyAllWindows()
    if cap is not None:
        cap.release()
