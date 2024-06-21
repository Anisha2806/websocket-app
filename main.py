from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import subprocess
import asyncio
import time

# Create an instance of FastAPI
app = FastAPI()

# Define your routes and endpoints
@app.get("/")
async def root():
    async def generate():
        for i in range(10):
            yield b"hello world\n"
            time.sleep(1)  # Simulate delay between messages

    return StreamingResponse(generate(), media_type="text/plain")

# WebSocket handler function to run a script and send output
async def run_script(websocket: WebSocket):
    process = await asyncio.create_subprocess_exec(
        "python", "runner.py",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    while True:
        line = await process.stdout.readline()
        if line:
            await websocket.send_text(line.decode().strip())
        else:
            break

# WebSocket endpoint to handle connections
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    await run_script(websocket)  # Call the function to run the script and send output
    await websocket.close()  # Close the WebSocket connection when done
