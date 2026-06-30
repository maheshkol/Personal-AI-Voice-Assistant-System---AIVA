import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

# Test if app loads
print("Loading websocket_server...")
import aiva.web.websocket_server as ws
print(f"app object: {ws.app}")
print(f"app type: {type(ws.app)}")
print("✅ App loaded successfully!")