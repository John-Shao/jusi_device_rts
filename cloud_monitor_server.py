import json
import logging
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from connection_manager import connectionManager


logger = logging.getLogger(__name__)

cloud_monitor_router = APIRouter()

@cloud_monitor_router.post("/cloud-monitor/online")
async def cloud_monitor_handler(request: dict):
    try:
        connectionManager._active_connections


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
'''