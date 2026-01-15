import cv2
import json
import time
import threading
import tempfile
from fastmrz import FastMRZ

fast_mrz = FastMRZ()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

FRAME_INTERVAL = 0.3
latest_frame = None
mrz_result = None
stop_scanning = False

def mrz_worker():
    global mrz_result, stop_scanning, latest_frame

    last_processed = 0
    print("MRZ worker started", flush=True)

    while not stop_scanning:
        # Wait until we have a frame
        if latest_frame is None:
            time.sleep(0.01)
            continue

        # Rate limiting to save CPU
        now = time.time()
        if now - last_processed < FRAME_INTERVAL:
            time.sleep(0.01)
            continue

        last_processed = now

        try:
            # Save current frame to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                cv2.imwrite(tmpfile.name, latest_frame)
                result = fast_mrz.get_details(tmpfile.name)

            # --- CORRECTION IS HERE ---
            # We check if result is a dict AND strictly ensure status is not FAILURE
            if isinstance(result, dict):
                # .get() returns None if 'status' key doesn't exist (which implies success in some versions)
                # or the actual value. We strictly check it's not 'FAILURE'.
                if result.get('status') != 'FAILURE':
                    mrz_result = result
                    stop_scanning = True
                    print("\nSUCCESS - MRZ DETECTED:", flush=True)
                    print(json.dumps(result, indent=4), flush=True)
                    return
                else:
                    # Optional: Print failure to debug stream, but don't stop scanning
                    # print("Scanning... (No MRZ found in this frame)", flush=True)
                    pass

        except Exception as e:
            print("OCR error:", str(e), flush=True)

# Start worker thread
threading.Thread(target=mrz_worker, daemon=True).start()

print("Camera started. Align passport MRZ code with camera...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    latest_frame = frame.copy()

    # Visual feedback
    if mrz_result:
        # Draw Green Box / Text when found
        cv2.rectangle(frame, (0, 0), (640, 80), (0, 255, 0), -1)
        cv2.putText(
            frame,
            "MRZ CAPTURED - CHECK CONSOLE",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2
        )
    else:
        # Draw instructions while scanning
        cv2.putText(
            frame,
            "Scanning...",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv2.imshow("Passport Scanner (press q to quit)", frame)

    # Quit on 'q' or if we want to stop automatically after scan
    # remove `or stop_scanning` if you want to keep video open after scan
    if (cv2.waitKey(1) & 0xFF == ord("q")) or stop_scanning:
        # Give a brief delay if stopping automatically so user sees the green success message
        if stop_scanning:
            cv2.imshow("Passport Scanner (press q to quit)", frame)
            cv2.waitKey(2000)
        break

cap.release()
cv2.destroyAllWindows()