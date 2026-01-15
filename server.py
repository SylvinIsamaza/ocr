
import os
import tempfile
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastmrz import FastMRZ

app = FastAPI()

# Initialize FastMRZ once
fast_mrz = FastMRZ()


@app.websocket("/ws/mrz-scanner")
async def mrz_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        while True:
            # 1. Receive image bytes from client
            data = await websocket.receive_bytes()

            # 2. FastMRZ usually requires a file path.q
            # We write the received bytes to a temp file.
            temp_filename = ""
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    tmp_file.write(data)
                    temp_filename = tmp_file.name

                # 3. Run OCR
                result = fast_mrz.get_details(temp_filename)

                # 4. Check logic: Ensure result is valid and NOT 'FAILURE'
                success = False
                if isinstance(result, dict) and result.get('status') != 'FAILURE':
                    success = True

                # 5. Send response back to client
                if success:
                    await websocket.send_json({
                        "status": "success",
                        "data": result
                    })
                else:
                    await websocket.send_json({
                        "status": "scanning",
                        "message": "No MRZ found"
                    })

            except Exception as e:
                print(f"Error processing frame: {e}")
                await websocket.send_json({"status": "error", "message": str(e)})

            finally:
                # Cleanup: Delete the temp file to save disk space
                if temp_filename and os.path.exists(temp_filename):
                    os.remove(temp_filename)

    except WebSocketDisconnect:
        print("Client disconnected")