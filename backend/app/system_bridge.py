from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.system_control import system_control_matrix
from app.security.sentinel_parser import SentinelParser
import logging

logger = logging.getLogger("JARVIS.SystemBridge")
router = APIRouter(prefix="/system", tags=["SystemControl"])
sentinel = SentinelParser()

class VolumeRequest(BaseModel):
    level: float

class BrightnessRequest(BaseModel):
    level: int

@router.post("/volume")
async def set_system_volume(request: VolumeRequest):
    # Security Validation via SentinelParser
    cmd_str = f"set_volume {request.level}"
    if not sentinel.validate_command(cmd_str):
        logger.warning(f"Sentinel blocked volume request: {cmd_str}")
        raise HTTPException(status_code=403, detail="Security Violation: Command blocked by Sentinel")

    result = system_control_matrix.set_volume(request.level)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/brightness")
async def set_system_brightness(request: BrightnessRequest):
    # Security Validation via SentinelParser
    cmd_str = f"set_brightness {request.level}"
    if not sentinel.validate_command(cmd_str):
        logger.warning(f"Sentinel blocked brightness request: {cmd_str}")
        raise HTTPException(status_code=403, detail="Security Violation: Command blocked by Sentinel")

    result = system_control_matrix.set_brightness(request.level)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/screenshot")
async def take_screenshot():
    # Security Validation via SentinelParser
    cmd_str = "capture_screens"
    if not sentinel.validate_command(cmd_str):
        logger.warning(f"Sentinel blocked screenshot request: {cmd_str}")
        raise HTTPException(status_code=403, detail="Security Violation: Command blocked by Sentinel")

    result = system_control_matrix.capture_screens()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/status")
async def get_system_status():
    # Security Validation via SentinelParser
    cmd_str = "get_hardware_status"
    if not sentinel.validate_command(cmd_str):
        logger.warning(f"Sentinel blocked status request: {cmd_str}")
        raise HTTPException(status_code=403, detail="Security Violation: Command blocked by Sentinel")

    result = system_control_matrix.get_hardware_status()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    # Include spatial awareness in general status
    spatial = system_control_matrix.get_spatial_awareness()
    result["data"]["spatial_awareness"] = spatial.get("monitors", [])

    return result
