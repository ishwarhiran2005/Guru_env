"""
OpenEnv Server Application.

This module provides the FastAPI server for OpenEnv deployment.
Implements the required /reset and /step endpoints.
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from env.sos_env import SOSEnv
from env.models import Action, Observation, Reward

# Create FastAPI app
app = FastAPI(
    title="SOS Environment - OpenEnv Server",
    description="Student Optimization System RL Environment",
    version="2.0.0"
)

# Global environment instance
env_instance: SOSEnv = None


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "name": "SOS Environment",
        "version": "2.0.0",
        "status": "running",
        "endpoints": ["/reset", "/step", "/state"]
    }


@app.post("/reset")
async def reset() -> Dict[str, Any]:
    """Reset the environment and return initial observation."""
    global env_instance
    
    try:
        # Create new environment instance
        env_instance = SOSEnv(max_steps=15, randomize=False)
        
        # Reset and get initial observation
        observation = await env_instance.reset()
        
        # Convert Pydantic model to dict
        return observation.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
async def step(action: Action) -> Dict[str, Any]:
    """Execute an action and return observation, reward, done, info."""
    global env_instance
    
    if env_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first."
        )
    
    try:
        # Execute step
        observation, reward_obj = await env_instance.step(action)
        
        # Return response in OpenEnv format
        return {
            "observation": observation.model_dump(),
            "reward": reward_obj.reward,
            "done": reward_obj.done,
            "info": reward_obj.info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """Get current environment state."""
    global env_instance
    
    if env_instance is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first."
        )
    
    try:
        state = env_instance.state()
        return state
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
