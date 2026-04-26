from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
from datetime import datetime

app = FastAPI(title="CyberShield SOC API", description="Real-time community cyber threat reporting backend.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "operational", "system_status": "SECURE", "threat_level": "ELEVATED"}

@app.post("/api/scan")
async def execute_scan(target: str):
    """
    Orchestrates scan across VirusTotal, AbuseIPDB, and Claude AI.
    Currently returns mocked responses for UI demonstration.
    """
    return {
        "target": target,
        "threatScore": random.randint(70, 98),
        "verdict": random.choice(["SUSPICIOUS", "DANGEROUS"]),
        "report": "[AI ANALYSIS]\nThe provided target matches patterns consistent with recent spear-phishing campaigns. Domain age is extremely low, and the SSL certificate originates from a free tier issuer not typically associated with legitimate financial institutions.\n\nRecommendation: DO NOT INTERACT. Flag as dangerous."
    }

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/api/feed/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for the live threat feed.
    In production, this subscribes to a Redis channel and pushes updates to frontend clients.
    """
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(4.5)
            threat = {
                "id": str(random.randint(10000, 99999)),
                "type": random.choice(["Phishing", "Malware", "Scam", "Suspicious IP"]),
                "target": f"10.2.{random.randint(0,255)}.{random.randint(0,255)}",
                "severity": random.choice(["DANGEROUS", "SUSPICIOUS"]),
                "timestamp": datetime.utcnow().isoformat(),
                "countryCode": random.choice(["RU", "CN", "US", "IR", "KP"]),
                "upvotes": random.randint(1, 50)
            }
            await websocket.send_text(json.dumps(threat))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
