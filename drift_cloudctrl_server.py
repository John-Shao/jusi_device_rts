import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from config import settings
from cloud_message_handler import handle_control_message


logger = logging.getLogger(__name__)

drift_cloudctrl_router = APIRouter()

# 设备云控API
@drift_cloudctrl_router.post("/cloud-control/{device_id}")
async def drift_cloud_control_handler(device_id: str, request: dict):
    try:
        connection_id = device_id
        logger.debug(f"发送控制消息: {json.dumps(request, indent=2)}")
        # 处理控制消息
        response = await handle_control_message(connection_id, request)
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





'''
# 获取在线设备列表
@app.get("/api/devices")
async def get_online_devices(room_id: Optional[str] = None):
    """获取在线设备列表"""
    devices = manager.get_online_devices(room_id)
    return {
        "code": 0,
        "data": devices,
        "count": len(devices)
    }

# 健康检查
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "connected_devices": len(manager.active_connections)
    }

# 截图上传端点（用于接收设备上传的截图）
@app.post("/api/upload/screenshot")
async def upload_screenshot_endpoint(data: dict):
    """接收设备上传的截图"""
    try:
        # 这里可以添加额外的验证逻辑
        # 例如验证 deviceId 是否合法等
        
        # 简单示例：直接返回成功
        return {
            "code": 0,
            "message": "截图上传成功",
            "data": {
                "url": f"/screenshots/{data.get('deviceId')}/{data.get('screenName', 'screenshot.jpg')}",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"处理截图上传时出错: {e}")
        return {
            "code": -1,
            "error_msg": str(e)
        }
'''