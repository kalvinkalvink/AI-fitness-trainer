# AI-fitness-trainer

The **AI Fitness Trainer** is a Python-based application designed to assist users in monitoring and improving their exercise form using real-time pose detection. This project utilizes computer vision techniques with OpenCV and MediaPipe to track body movements during various exercises, providing feedback on performance and counting repetitions.

## Features

- **Real-time Pose Detection**: Utilizes MediaPipe to detect body landmarks and calculate angles for various exercises.
  
- **Exercise Tracking**: Supports multiple exercises including push-ups, squats, jumping jacks, sit-ups, and lunges, with real-time feedback on form and repetitions.

- **User Interface**: A simple graphical user interface (GUI) built with Tkinter for exercise selection and control.

- **Visual Feedback**: Provides visual cues for maintaining proper form and alignment during exercises.

## Requirements

To run this project, ensure you have the following installed:

- Python 3.x
- OpenCV
- NumPy
- MediaPipe
- Tkinter (usually included with Python installations)

You can install the required packages using pip:

```bash
pip install opencv-python numpy mediapipe
```

### Setup with uv (recommended)

This project ships `pyproject.toml` and `uv.lock` so the environment is reproducible.
[uv](https://docs.astral.sh/uv/) manages the Python version (3.12) and all dependencies.

1. Install uv (if needed):

   ```bash
   curl -LsSf astral.sh/uv/install.sh | sh
   ```

2. Sync the locked environment:

   ```bash
   uv sync
   ```

3. Run the app:

   ```bash
   uv run main.py
   ```

   (`uv run camera4.py` also works — it is a backward-compat shim that calls into `main.py`.)

Notes:

- `mediapipe` is pinned to `==0.10.21` because MediaPipe 1.x removed the
  `mp.solutions` API that `PoseModule.py` uses. Do not upgrade it without
  migrating to `mp.tasks.vision.PoseLandmarker`.
- The app probes camera indices 0-4 at startup and uses the first one that
  returns frames, so a webcam on `/dev/video1` (or similar) works without
  code changes. Use the Stop button (or press `q` in the video window) to end
  a session.

## File Structure

- **`main.py`**: Entry point — run with `uv run main.py` (`uv run camera4.py` also works via a backward-compat shim).
- **`app.py`**: `ExerciseApp` Tk GUI (exercise selection, Start/Stop, session threading).
- **`session.py`**: `run_session()` capture loop — frame grab, pose detection, rep overlay, `q`-to-stop.
- **`camera.py`**: `open_camera()` — probes camera indices 0-4, returns the first one delivering frames.
- **`pose_detector.py`**: `PoseDetector` — MediaPipe landmarks, positions, joint angles.
- **`tracker.py`**: `ExerciseTracker` — angle smoothing for stable rep counting.
- **`exercises/`**: One module per exercise plus a registry (`EXERCISES`, `get()`):
  `pushups.py`, `squats.py`, `jumping_jacks.py`, `situps.py`, `lunges.py`.
  To add an exercise, create `exercises/my_move.py` with `NAME` and
  `logic(img, lmlist, count, dir, tracker)`, then register it in
  `exercises/__init__.py`.
- **`camera4.py` / `PoseModule.py`**: Backward-compat shims re-exporting `main` / `PoseDetector`.

## Usage

### Running the Application

1. Ensure your webcam is connected and accessible.

2. Run the main application file:

   ```bash
   uv run main.py
   ```

   (Without uv: `python main.py` after `pip install opencv-python numpy mediapipe`.
   `camera4.py` remains as a working alias.)

3. Upon launching, a GUI will appear allowing you to select an exercise from the dropdown menu.

4. Click the "Start Exercise" button to begin tracking your selected exercise. The application will provide real-time feedback on your performance.

5. Press 'q' in the video window or click "Stop" to end the session; use "Quit" (or close the window) to exit the app.

### Supported Exercises

The application currently supports the following exercises:

- Push-ups
- Squats
- Jumping Jacks
- Sit-ups
- Lunges

Each exercise has specific criteria for counting repetitions based on joint angles and body alignment.

## Functionality Detail

### Pose Detection

The `PoseModule.py` file contains a class `poseDetector` that implements methods for:
  
- Finding poses in images.
- Extracting landmark positions.
- Calculating angles between specified body points.

The angles are crucial for determining if the user is performing exercises correctly. 

### Exercise Logic

In `camera4.py`, each exercise has its own logic function (e.g., `push_up_logic`, `squats_logic`, etc.) that:

- Calculates necessary angles for proper form.
- Counts repetitions based on angle thresholds.
- Provides visual feedback on performance through progress bars and text messages displayed on the video feed.

### GUI Implementation

The Tkinter-based GUI allows users to:
  
- Select an exercise from a dropdown menu.
- Start or quit the exercise session easily.

## Contribution

Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request with your changes. 

## License

This project is licensed under the MIT License - see the LICENSE file for details.
