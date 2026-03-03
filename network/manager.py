"""
네트워크 매니저
BLE / WiFi 통신을 통합 관리
자동 전환 및 메시지 라우팅
"""
import queue
import threading
import time

from network.ble_central import BLECentral
from network.ble_peripheral import BLEPeripheral
from network.wifi_socket import WiFiServer, WiFiClient, WiFiDiscovery
from network.protocol import (
    Message, make_hello, make_bye, make_pet_info,
    make_battle_request, make_battle_choice,
)
from data.constants import WIFI_DEFAULT_PORT, MSG_HELLO, MSG_BYE


class NetworkManager:
    """통합 네트워크 매니저"""

    def __init__(self, pet=None):
        self.pet = pet
        self.message_queue = queue.Queue()  # 공유 메시지 큐

        # BLE
        self.ble_central = BLECentral(self.message_queue)
        self.ble_peripheral = BLEPeripheral(
            pet_data_provider=self._get_pet_data,
            message_queue=self.message_queue,
        )

        # WiFi
        self.wifi_server = WiFiServer(WIFI_DEFAULT_PORT, self.message_queue)
        self.wifi_client = WiFiClient(self.message_queue)
        self.wifi_discovery = WiFiDiscovery(message_queue=self.message_queue)

        # 상태
        self.mode = None       # "ble", "wifi", None
        self.connected = False
        self.peer_info = None   # 연결된 상대 펫 정보

        # 콜백
        self.on_message = None     # callback(message)
        self.on_connected = None   # callback(peer_info)
        self.on_disconnected = None
        self.on_error = None       # callback(error_msg)
        self.on_peer_found = None  # callback(peer_info)

    def _get_pet_data(self):
        """BLE Peripheral용 펫 데이터 제공"""
        if self.pet:
            return self.pet.get_brief_info()
        return {}

    def set_pet(self, pet):
        self.pet = pet

    # ─── BLE 동작 ───

    def start_ble_scan(self, duration=5.0):
        """BLE 스캔 시작"""
        self.ble_central.start()
        self.ble_central.scan(duration)

    def start_ble_peripheral(self):
        """BLE 서버 시작 (광고)"""
        self.ble_peripheral.start()

    def connect_ble(self, address):
        """BLE 기기에 연결"""
        self.ble_central.connect(address)
        self.mode = "ble"

    # ─── WiFi 동작 ───

    def start_wifi_server(self):
        """WiFi 서버 시작 (수신 대기)"""
        self.wifi_server.start()
        self.wifi_discovery.start_listening()
        # 주기적 브로드캐스트
        self._start_wifi_broadcast()

    def connect_wifi(self, host, port=WIFI_DEFAULT_PORT):
        """WiFi 서버에 연결"""
        self.wifi_client.connect(host, port)
        self.mode = "wifi"

    def _start_wifi_broadcast(self):
        """주기적으로 WiFi 브로드캐스트"""
        def _broadcast_loop():
            while self.wifi_server.running:
                if self.pet:
                    self.wifi_discovery.broadcast(
                        self.pet.get_brief_info(),
                        WIFI_DEFAULT_PORT,
                    )
                time.sleep(3)

        t = threading.Thread(target=_broadcast_loop, daemon=True)
        t.start()

    # ─── 메시지 전송 ───

    def send(self, message):
        """현재 모드에 맞춰 메시지 전송"""
        if self.mode == "ble":
            if self.ble_central.connected:
                return self.ble_central.send(message)
            elif self.ble_peripheral.advertising:
                self.ble_peripheral.notify(message)
                return True
        elif self.mode == "wifi":
            if self.wifi_client.connected:
                return self.wifi_client.send(message)
            elif self.wifi_server.running:
                self.wifi_server.broadcast(message)
                return True
        return False

    def send_hello(self):
        """인사 메시지 전송"""
        if self.pet:
            self.send(make_hello(self.pet))

    def send_pet_info(self):
        """펫 정보 전송"""
        if self.pet:
            self.send(make_pet_info(self.pet))

    def send_battle_request(self):
        """배틀 요청 전송"""
        if self.pet:
            self.send(make_battle_request(self.pet))

    def send_battle_choice(self, choice):
        """배틀 선택 전송"""
        self.send(make_battle_choice(choice))

    # ─── 메시지 큐 처리 ───

    def process_messages(self):
        """메인 루프에서 호출 - 큐에 쌓인 메시지 처리"""
        processed = []
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
                self._handle_internal_message(msg)
                processed.append(msg)
            except queue.Empty:
                break
        return processed

    def _handle_internal_message(self, msg):
        """내부 시스템 메시지 처리"""
        msg_type = msg.get("type", "")

        # BLE 이벤트
        if msg_type == "ble_connected":
            self.connected = True
            self.mode = "ble"
            # 자동 인사
            self.send_hello()
            if self.on_connected:
                self.on_connected(msg.get("data"))

        elif msg_type == "ble_disconnected":
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected()

        elif msg_type == "ble_device_found":
            if self.on_peer_found:
                self.on_peer_found(msg.get("data"))

        elif msg_type == "ble_message":
            self._handle_game_message(msg.get("data"))

        # WiFi 이벤트
        elif msg_type == "wifi_connected":
            self.connected = True
            self.mode = "wifi"
            self.send_hello()
            if self.on_connected:
                self.on_connected(msg.get("data"))

        elif msg_type == "wifi_client_connected":
            self.connected = True
            if self.on_connected:
                self.on_connected(msg.get("data"))

        elif msg_type == "wifi_disconnected" or msg_type == "wifi_client_disconnected":
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected()

        elif msg_type == "wifi_message":
            self._handle_game_message(msg.get("data"))

        elif msg_type == "wifi_peer_found":
            if self.on_peer_found:
                self.on_peer_found(msg.get("data"))

        # 오류
        elif msg_type.endswith("_error"):
            error = msg.get("data", {}).get("error", "알 수 없는 오류")
            if self.on_error:
                self.on_error(error)

    def _handle_game_message(self, message):
        """게임 메시지 처리"""
        if isinstance(message, Message):
            if message.type == MSG_HELLO:
                self.peer_info = message.data.get("pet_info", {})
                # 자동 응답
                self.send_pet_info()

            if self.on_message:
                self.on_message(message)

    # ─── 정리 ───

    def stop_all(self):
        """모든 네트워크 서비스 중지"""
        try:
            self.send(make_bye())
        except Exception:
            pass

        self.ble_central.stop()
        self.ble_peripheral.stop()
        self.wifi_server.stop()
        self.wifi_client.disconnect()
        self.wifi_discovery.stop()
        self.connected = False

    @property
    def is_connected(self):
        return self.connected or self.ble_central.connected or self.wifi_client.connected

    def get_status(self):
        """현재 네트워크 상태 문자열"""
        if self.connected:
            peer_name = self.peer_info.get("name", "???") if self.peer_info else "???"
            return f"연결됨 ({self.mode}) - {peer_name}"
        elif self.ble_central.scanning:
            return "블루투스 검색 중..."
        elif self.wifi_server.running:
            return "WiFi 대기 중..."
        return "연결 안됨"
