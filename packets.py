import json
from typing import Any, Dict

def pack(msg: Dict[str, Any]) -> bytes:
    return json.dumps(msg, ensure_ascii=False).encode("utf-8")

def unpack(data: bytes) -> Dict[str, Any]:
    return json.loads(data.decode("utf-8"))