import logging
from typing import Optional
from models import (
    ControlMessage, EventType, MessageType
)
from connection_manager import connectionManager


logger = logging.getLogger(__name__)

# 处理会议系统发送的控制消息
async def handle_control_message(device_id: str, request: dict) -> Optional[dict]:
    """处理控制消息"""
    try:
        # 解析控制消息
        ctrl_msg = ControlMessage(**request)
        
        handler = HANDLER_MAP.get(ctrl_msg.event)
        if handler:
            return await handler(ctrl_msg, device_id)
        else:
            raise ValueError(f"未知的控制事件: {ctrl_msg.event}")
            
    except Exception as e:
        logger.error(f"处理控制消息时出错: {e}")
        return {
            "type": "notify",
            "event": ctrl_msg.event if 'control_msg' in locals() else "unknown",
            "playId": ctrl_msg.playId,
            "deviceId": ctrl_msg.deviceId,
            "code": -1,
            "error_msg": str(e)
        }


async def handle_device_info(
    message: ControlMessage,
    device_id: str
    ) -> dict:
    """获取设备信息"""

    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.DEVICE_INFO,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    response = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if response else -1,
        "type": MessageType.CONTROL,
        "event": EventType.DEVICE_INFO,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if response else "failed"}
    }    
    

async def handle_start_rtsp(
    message: ControlMessage,
    device_id: str
    ) -> dict:
    """处理开始 RTMP 推流"""
    if "rtmp_url" not in message.data:
        raise ValueError("缺少 rtmp_url 参数")

    # 构建控制消息
    ctrl_msg = {
        "type": message.type,
        "event": message.event,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": message.data
    }
    
    result = await connectionManager.send_message(device_id, ctrl_msg)

    # 更新设备状态
    if result:
        device_status = connectionManager._device_status.get(device_id)
        if device_status:
            device_status.video_pushing = True
            device_status.rtmp_url = message.data["rtmp_url"]
    
    return {
        "code": 0 if result else -1,
        "type": MessageType.CONTROL,
        "event": EventType.START_RTMP,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


async def handle_stop_rtsp(
    message: ControlMessage,
    device_id: str
    ) -> dict:
    """处理停止 RTMP 推流"""
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RTMP,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    # 更新设备状态
    if result:
        device_status = connectionManager._device_status.get(device_id)
        if device_status:
            device_status.video_pushing = False

    return {
        "code": 0 if result else -1,
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RTMP,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


async def _handle_start_rtsp(
    message: ControlMessage,
    device_id: str
    ) -> dict:
    """处理开始 RTSP 语音接收"""
    data = message.data or {}
    
    if "rtsp_url" not in data:
        raise ValueError("缺少 rtsp_url 参数")
    
    
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.START_RTSP,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": data
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    # 更新设备状态
    device_status = connectionManager._device_status.get(device_id)
    if device_status:
        device_status.audio_pulling = True
        device_status.rtsp_url = data["rtsp_url"]
    
    return {
        "type": MessageType.CONTROL,
        "event": EventType.START_RTSP,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "code": 0,
        "data": {"status": "success" if result else "failed"}
    }


async def _handle_stop_rtsp(
    message: ControlMessage,
    device_id: str
    ) -> dict:
    """处理停止 RTSP 语音接收"""
    
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RTSP,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    # 更新设备状态
    if result:
        device_status = connectionManager._device_status.get(device_id)
        if device_status:
            device_status.audio_pulling = False

    return {
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RTSP,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "code": 0,
        "data": {"status": "success" if result else "failed"}
    }


async def handle_start_record(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理开始录像"""
    # 更新设备状态
    device_status = connectionManager._device_status.get(device_id)
    if device_status:
        device_status.recording = True
    
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.START_RECORD,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": MessageType.CONTROL,
        "event": EventType.START_RECORD,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


async def handle_stop_record(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理停止录像"""
    # 更新设备状态
    device_status = connectionManager._device_status.get(device_id)
    if device_status:
        device_status.recording = False
    
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RECORD,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": MessageType.CONTROL,
        "event": EventType.STOP_RECORD,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


async def handle_dzoom(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理数字变焦控制"""
    data = message.data or {}
    
    if "dzoom" not in data:
        raise ValueError("缺少 dzoom 参数")
    
    dzoom_value = data["dzoom"]
    if not isinstance(dzoom_value, int) or dzoom_value < 0:
        raise ValueError("dzoom 参数必须是正整数")
    
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.DZOOM,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": data
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": MessageType.CONTROL,
        "event": EventType.DZOOM,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"dzoom": dzoom_value,
                    "status": "success" if result else "failed"}
    }


async def handle_stream_res(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理设置分辨率"""
    data = message.data or {}
    
    if "stream_res" not in data:
        raise ValueError("缺少 stream_res 参数")
    
    stream_res = data["stream_res"]
    
    # 验证分辨率
    resolution_map = {
        0: "4K",
        1: "4KUHD",
        2: "2.7K",
        3: "1080P",
        4: "720P",
        5: "WVGA"
    }
    
    if isinstance(stream_res, int):
        if stream_res not in resolution_map:
            raise ValueError(f"不支持的分辨率代码: {stream_res}")
        stream_res = resolution_map[stream_res]
    elif isinstance(stream_res, str):
        if stream_res not in resolution_map.values():
            raise ValueError(f"不支持的分辨率: {stream_res}")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "stream_res",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_res": stream_res}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "stream_res",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_res": stream_res,
                    "status": "success" if result else "failed"}
    }


async def handle_stream_bitrate(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理设置比特率"""
    data = message.data or {}
    
    if "stream_bitrate" not in data:
        raise ValueError("缺少 stream_bitrate 参数")
    
    bitrate = data["stream_bitrate"]
    if not isinstance(bitrate, int) or bitrate <= 0 or bitrate > 4000000:
        raise ValueError("比特率必须在 1-4000000 之间")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "stream_bitrate",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_bitrate": bitrate}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "stream_bitrate",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_bitrate": bitrate,
                    "status": "success" if result else "failed"}
    }


async def handle_stream_framerate(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理设置帧率"""
    data = message.data or {}
    
    if "stream_framerate" not in data:
        raise ValueError("缺少 stream_framerate 参数")
    
    framerate = data["stream_framerate"]
    if not isinstance(framerate, int) or framerate <= 0 or framerate > 120:
        raise ValueError("帧率必须在 1-120 之间")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "stream_framerate",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_framerate": framerate}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "stream_framerate",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"stream_framerate": framerate,
                    "status": "success" if result else "failed"}
    }


async def handle_led(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理 LED 控制"""
    data = message.data or {}
    
    if "led" not in data:
        raise ValueError("缺少 led 参数")
    
    led_value = data["led"]
    if led_value not in [0, 1]:
        raise ValueError("led 参数必须是 0 或 1")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "led",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"led": led_value}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "led",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"led": led_value,
                    "status": "success" if result else "failed"}
    }


async def handle_exposure(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理曝光设置"""
    data = message.data or {}
    
    if "exposure" not in data:
        raise ValueError("缺少 exposure 参数")
    
    exposure_value = data["exposure"]
    if exposure_value not in [0, 1, 2, 3, 4]:
        raise ValueError("exposure 参数必须是 0-4")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "exposure",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"exposure": exposure_value}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "exposure",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"exposure": exposure_value,
                    "status": "success" if result else "failed"}
    }


async def handle_filter(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理滤镜设置"""
    data = message.data or {}
    
    if "filter" not in data:
        raise ValueError("缺少 filter 参数")
    
    filter_value = data["filter"]
    if filter_value not in [0, 1, 2]:
        raise ValueError("filter 参数必须是 0-2")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "filter",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"filter": filter_value}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "filter",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"filter": filter_value,
                    "status": "success" if result else "failed"}
    }


async def handle_mic_sensitivity(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理麦克风灵敏度设置"""
    data = message.data or {}
    
    if "mic_sensitivity" not in data:
        raise ValueError("缺少 mic_sensitivity 参数")
    
    sensitivity = data["mic_sensitivity"]
    if sensitivity not in [0, 1, 2, 3, 4, 5]:
        raise ValueError("mic_sensitivity 参数必须是 0-5")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "mic_sensitivity",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"mic_sensitivity": sensitivity}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "mic_sensitivity",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"mic_sensitivity": sensitivity,
                    "status": "success" if result else "failed"}
    }


async def handle_fov(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理视场角设置"""
    data = message.data or {}
    
    if "fov" not in data:
        raise ValueError("缺少 fov 参数")
    
    fov_value = data["fov"]
    if fov_value not in [90, 110, 140]:
        raise ValueError("fov 参数必须是 90, 110 或 140")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "fov",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"fov": fov_value}
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "fov",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"fov": fov_value,
                    "status": "success" if result else "failed"}
    }


async def handle_screen(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理截图命令"""
    data = message.data or {}
    
    required_fields = ["screenName", "url", "roomId"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少 {field} 参数")
    
    # 发送控制消息到设备
    control_msg = {
        "type": "control",
        "event": "screen",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": data
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else -1,
        "type": "notify",
        "event": "screen",
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


async def handle_power_off(
    message: ControlMessage,
    device_id: str
) -> dict:
    """处理关机命令"""
    # 发送控制消息到设备
    control_msg = {
        "type": MessageType.CONTROL,
        "event": EventType.POWER_OFF,
        "playId": message.playId,
        "deviceId": message.deviceId
    }
    
    result = await connectionManager.send_message(device_id, control_msg)
    
    return {
        "code": 0 if result else 1,
        "type": MessageType.CONTROL,
        "event": EventType.POWER_OFF,
        "playId": message.playId,
        "deviceId": message.deviceId,
        "data": {"status": "success" if result else "failed"}
    }


# 处理程序映射
HANDLER_MAP = {
    EventType.DEVICE_INFO: handle_device_info,
    EventType.START_RTMP: handle_start_rtsp,
    EventType.STOP_RTMP: handle_stop_rtsp,
    EventType.START_RTSP: handle_start_rtsp,
    EventType.STOP_RTSP: handle_stop_rtsp,
    EventType.START_RECORD: handle_start_record,
    EventType.STOP_RECORD: handle_stop_record,
    EventType.DZOOM: handle_dzoom,
    EventType.STREAM_RES: handle_stream_res,
    EventType.STREAM_BITRATE: handle_stream_bitrate,
    EventType.STREAM_FRAMERATE: handle_stream_framerate,
    EventType.LED: handle_led,
    EventType.EXPOSURE: handle_exposure,
    EventType.FILTER: handle_filter,
    EventType.MIC_SENSITIVITY: handle_mic_sensitivity,
    EventType.FOV: handle_fov,
    EventType.SCREEN: handle_screen,
    EventType.POWER_OFF: handle_power_off,
}
