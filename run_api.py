import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

# Direct import of the app object
import aiva.web.websocket_server as ws_module
app = ws_module.app

import uvicorn

if __name__ == "__main__":
    print("Starting AIVA API Server...")
    print("URL: http://localhost:8080")
    print("Docs: http://localhost:8080/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False
    )