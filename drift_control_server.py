import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from config import settings
from cloud_control_handler import handle_control_message


logger = logging.getLogger(__name__)

drift_cloudctrl_router = APIRouter()

# 设备云控API
@drift_cloudctrl_router.post("/cloud-control/{device_id}")
async def drift_cloud_control_handler(device_id: str, request: dict):
    try:
        logger.debug(f"发送控制消息: {json.dumps(request, indent=2)}")
        # 处理控制消息
        response = await handle_control_message(device_id, request)
        logger.debug(f"控制命令响应: {json.dumps(response, indent=2)}")
        
        if response and response.get("code"):
            raise HTTPException(
                status_code=400,
                detail=response.get("error_msg", "控制命令执行失败")
            )
        return JSONResponse(content=response or {})
    except Exception as e:
        logger.error(f"发送控制命令时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))
