import json
import logging
from typing import Optional
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from models import MonitorMsgType, MonitorRequest, MonitorResponse
from connection_manager import connectionManager


logger = logging.getLogger(__name__)

cloud_monitor_router = APIRouter()

@cloud_monitor_router.post("/online-monitor")
async def cloud_monitor_handler(request: dict):
    try:
        monitor_request = MonitorRequest(**request)
        response = await handle_monitor_message(monitor_request)
        return JSONResponse(content=response or {})
    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 处理监视消息
async def handle_monitor_message(request: MonitorRequest) -> Optional[MonitorResponse]:
    try:
        handler = HANDLER_MAP.get(request.type)
        if handler:
            return await handler(request)
        else:
            raise ValueError(f"未知的控制事件: {request.type}")
    except Exception as e:
        logger.error(f"处理控制消息时出错: {e}")
        resp = MonitorResponse(
            type=request.type,
            code=500,
            info="处理控制消息时出错",
        )
        return resp.model_dump()


# 获取设备列表
async def handle_get_device_list(request: MonitorRequest) -> dict:
    device_list = connectionManager.get_device_list()
    resp = MonitorResponse(
        type=request.type,
        data=device_list,
    )
    return resp.model_dump()

# 获取设备状态
async def handle_get_device_status(request: MonitorRequest) -> dict:
    device_id = request.data.get("device_id")
    device_status = connectionManager.get_device_status(device_id)
    resp = MonitorResponse(
        type=request.type,
        data=device_status,
    )
    return resp.model_dump()

# 处理程序映射
HANDLER_MAP = {
    MonitorMsgType.GET_DEVICE_LIST: handle_get_device_list,
    MonitorMsgType.GET_DEVICE_STATUS: handle_get_device_status,
}
