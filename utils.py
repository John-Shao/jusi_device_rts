import time
import uuid


def current_timestamp_s() -> int:
    """获取当前时间戳"""
    return int(time.time())

def current_timestamp_ms() -> int:
    """获取当前时间戳"""
    return int(time.time() * 1000)

def generate_uuid() -> str:
    return str(uuid.uuid4()).replace("-", "")
