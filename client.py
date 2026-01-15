import cv2
import asyncio
import websockets
import json
import time

# Configuration
SERVER_URL = "ws://127.0.0.1:8000/ws/mrz-scanner"
FRAME_INTERVAL = 0.3  # How often to check the server


class MRZScanner:
    def __init__(self):
        self.latest_jpg_bytes = None
        self.scan_result = None
        self.stop_scanning = False
        self.is_connected = False

    async def network_loop(self):
        """
        Background task: Handles WebSocket connection, sending images,
        and receiving results. independent of the camera FPS.
        """
        print(f"Connecting to {SERVER_URL}...")
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                print("Connected to server!")
                self.is_connected = True

                while not self.stop_scanning:
                    # 1. Check if we have a frame to send
                    if self.latest_jpg_bytes and self.scan_result is None:
                        try:
                            # Send the image
                            await websocket.send(self.latest_jpg_bytes)

                            # Wait for response (This blocks THIS function, but not the camera)
                            response_str = await websocket.recv()
                            response = json.loads(response_str)

                            if response.get("status") == "success":
                                self.scan_result = response["data"]
                                print("\nSUCCESS - MRZ DETECTED:")
                                print(json.dumps(self.scan_result, indent=4))
                                self.stop_scanning = True

                        except Exception as e:
                            print(f"Network error: {e}")

                    # Wait a bit before sending the next frame to save bandwidth
                    await asyncio.sleep(FRAME_INTERVAL)

        except Exception as e:
            print(f"Connection failed: {e}")
        finally:
            self.is_connected = False

    async def start(self):
        """
        Main task: Handles Camera, UI drawing, and user input.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        # Start the network loop in the background
        network_task = asyncio.create_task(self.network_loop())

        print("Camera started. Press 'q' to quit.")

        while not self.stop_scanning:
            ret, frame = cap.read()
            if not ret:
                break

            # 1. Update the shared buffer for the network task
            # We compress here so the UI thread takes the hit,
            # but it ensures the network task just grabs and sends.
            _, buffer = cv2.imencode('.jpg', frame)
            self.latest_jpg_bytes = buffer.tobytes()

            # 2. Draw UI based on state
            if self.scan_result:
                # Success State
                cv2.rectangle(frame, (0, 0), (640, 80), (0, 255, 0), -1)
                cv2.putText(frame, "MRZ FOUND", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            else:
                # Scanning State
                if self.is_connected:
                    cv2.putText(frame, "Scanning...", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Connecting...", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow("Smooth MRZ Scanner", frame)

            # 3. Handle Quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.stop_scanning = True
                break

            # 4. CRITICAL: Yield control so network_task can run
            await asyncio.sleep(0.01)

        # Cleanup
        if self.scan_result:
            # Show the success screen for a few seconds before closing
            cv2.imshow("Smooth MRZ Scanner", frame)
            cv2.waitKey(3000)

        cap.release()
        cv2.destroyAllWindows()

        # Ensure network task finishes
        try:
            await network_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    scanner = MRZScanner()
    asyncio.run(scanner.start())