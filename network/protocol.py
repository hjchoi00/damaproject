"""
네트워크 프로토콜 정의
BLE / WiFi 공통 메시지 직렬화/역직렬화
"""
import json
import time
from data.constants import (
    MSG_HELLO, MSG_PET_INFO, MSG_GIFT, MSG_BATTLE_REQUEST,
    MSG_BATTLE_CHOICE, MSG_BATTLE_RESULT, MSG_BYE,
)


class Message:
    """네트워크 메시지"""

    def __init__(self, msg_type, data=None, sender_id=None):
        self.type = msg_type
        self.data = data or {}
        self.sender_id = sender_id
        self.timestamp = time.time()

    def to_json(self):
        """JSON 문자열로 직렬화"""
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "sender": self.sender_id,
            "ts": self.timestamp,
        }, ensure_ascii=False)

    def to_bytes(self):
        """바이트 직렬화 (네트워크 전송용)"""
        payload = self.to_json().encode("utf-8")
        # 길이 헤더 (4바이트) + 데이터
        length = len(payload)
        return length.to_bytes(4, "big") + payload

    @classmethod
    def from_json(cls, json_str):
        """JSON에서 메시지 복원"""
        try:
            d = json.loads(json_str)
            msg = cls(
                msg_type=d.get("type", "unknown"),
                data=d.get("data", {}),
                sender_id=d.get("sender"),
            )
            msg.timestamp = d.get("ts", time.time())
            return msg
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[PROTOCOL] Parse error: {e}")
            return None

    @classmethod
    def from_bytes(cls, data_bytes):
        """바이트에서 메시지 복원"""
        try:
            json_str = data_bytes.decode("utf-8")
            return cls.from_json(json_str)
        except Exception as e:
            print(f"[PROTOCOL] Decode error: {e}")
            return None

    def __repr__(self):
        return f"Message(type={self.type!r}, data={self.data})"


# ─── 편의 메시지 생성 함수 ───

def make_hello(pet):
    """인사 메시지 생성"""
    return Message(MSG_HELLO, {
        "pet_info": pet.get_brief_info(),
    }, sender_id=pet.owner_id)


def make_pet_info(pet):
    """펫 상세 정보 메시지"""
    return Message(MSG_PET_INFO, {
        "pet": pet.get_brief_info(),
        "happiness": int(pet.happiness),
        "health": int(pet.health),
    }, sender_id=pet.owner_id)


def make_battle_request(pet):
    """배틀 요청"""
    return Message(MSG_BATTLE_REQUEST, {
        "pet_info": pet.get_brief_info(),
    }, sender_id=pet.owner_id)


def make_battle_choice(choice):
    """배틀 선택 (가위바위보)"""
    return Message(MSG_BATTLE_CHOICE, {
        "choice": choice,  # 0=바위, 1=가위, 2=보
    })


def make_battle_result(result, score):
    """배틀 결과"""
    return Message(MSG_BATTLE_RESULT, {
        "result": result,
        "score": score,
    })


def make_gift(item_name):
    """선물 메시지"""
    return Message(MSG_GIFT, {
        "item": item_name,
    })


def make_bye():
    """연결 종료"""
    return Message(MSG_BYE)


# ─── BLE 데이터 분할 (20바이트 청크) ───

BLE_CHUNK_SIZE = 20


def split_for_ble(data_bytes):
    """BLE 전송을 위해 데이터를 20바이트 청크로 분할"""
    chunks = []
    total = len(data_bytes)
    num_chunks = (total + BLE_CHUNK_SIZE - 1) // BLE_CHUNK_SIZE

    for i in range(num_chunks):
        start = i * BLE_CHUNK_SIZE
        end = min(start + BLE_CHUNK_SIZE, total)
        # 헤더: [chunk_index, total_chunks]
        header = bytes([i, num_chunks])
        chunk = header + data_bytes[start:end]
        chunks.append(chunk)

    return chunks


def reassemble_ble(chunks_dict):
    """BLE 청크들을 재조립"""
    if not chunks_dict:
        return None

    total = max(chunks_dict.keys()) + 1
    if len(chunks_dict) < total:
        return None  # 아직 모든 청크가 안 왔음

    data = b""
    for i in range(total):
        if i not in chunks_dict:
            return None
        data += chunks_dict[i]

    return data
