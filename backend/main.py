"""
FastAPI server entrypoint for OMNIAI.

Endpoints:
- GET /             -> health check {"status":"OMNIAI running"}
- POST /run         -> run agent on provided goal (protected by token)
- GET /memory       -> returns last 20 memory entries (protected)
"""
from __future__ import annotations
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Any
import os

from . import planner, agent, memory, auth, utils

app = FastAPI(title="OMNIAI")
logger = utils.logger

# Allow local frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount frontend static files if they exist
if os.path.isdir("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

class RunRequest(BaseModel):
    goal: str

class RunResponse(BaseModel):
    goal: str
    steps: List[str]
    results: List[str]
    details: List[Any]
    recent_memory: List[Any]
    success: bool = True

@app.get("/")
def root():
    return {"status": "OMNIAI running"}

@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest, _: bool = Depends(auth.verify_token)):
    logger.info("Received run request for goal: %s", req.goal)
    steps = planner.plan(req.goal)
    execution = agent.execute(req.goal, steps)
    return RunResponse(
        goal=req.goal,
        steps=steps,
        results=execution["results"],
        details=execution["details"],
        recent_memory=execution.get("recent_memory", []),
        success=True,
    )

@app.get("/memory")
def get_memory(_: bool = Depends(auth.verify_token)):
    return {"memory": memory.load_last(20)}
