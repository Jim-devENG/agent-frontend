# How to Start the Backend Server

## Quick Start

1. **Open a terminal/PowerShell in the project root** (`C:\Users\MIKENZY\Documents\Apps\liquidcanvas`)

2. **Start the FastAPI backend:**
   ```powershell
   # Try one of these commands:
   py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # OR if that doesn't work:
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # OR if you have uvicorn installed globally:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **You should see output like:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

4. **Verify it's running:**
   - Open http://localhost:8000/docs in your browser
   - You should see the FastAPI Swagger documentation

5. **Keep this terminal open** - the server needs to stay running

## Troubleshooting

- **"Python was not found"**: Make sure Python is installed and in your PATH, or use `py` launcher
- **"Module not found"**: Run `pip install -r requirements.txt` first
- **Port 8000 already in use**: Stop any other process using port 8000, or change the port with `--port 8001`

## Frontend Connection

Once the backend is running, your frontend dashboard at http://localhost:3000 will automatically connect and the connection error banner will disappear.

