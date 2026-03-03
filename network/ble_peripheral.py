"""
BLE 통신 모듈 - Peripheral (광고/서버) 역할
Bless 라이브러리 사용
"""
import asyncio
import threading
import queue
from data.constants import BLE_SERVICE_UUID, BLE_CHAR_PET_DATA_UUID, BLE_CHAR_MESSAGE_UUID


class BLEPeripheral:
    """BLE Peripheral - GATT Server로 펫 데이터 광고"""

    def __init__(self, pet_data_provider=None, message_queue=None):
        self.pet_data_provider = pet_data_provider  # callable: () -> dict
        self.message_queue = message_queue or queue.Queue()
        self.advertising = False
        self.server = None
        self._loop = None
        self._thread = None

    def start(self):
        """서버 시작"""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_server())

    async def _start_server(self):
        """GATT 서버 시작"""
        try:
            from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties

            self.server = BlessServer(name="Damagochi")

            # 서비스 추가
            await self.server.add_new_service(BLE_SERVICE_UUID)

            # 펫 데이터 캐릭터리스틱 (읽기)
            await self.server.add_new_characteristic(
                BLE_SERVICE_UUID,
                BLE_CHAR_PET_DATA_UUID,
                GATTCharacteristicProperties.read,
                None,
                self._on_read_pet_data,
            )

            # 메시지 캐릭터리스틱 (쓰기 + 알림)
            await self.server.add_new_characteristic(
                BLE_SERVICE_UUID,
                BLE_CHAR_MESSAGE_UUID,
                GATTCharacteristicProperties.write | GATTCharacteristicProperties.notify,
                None,
                self._on_write_message,
            )

            # 광고 시작
            await self.server.start()
            self.advertising = True

            self.message_queue.put({
                "type": "ble_peripheral_started",
                "data": {}
            })

            # 서버 유지
            while self.advertising:
                await asyncio.sleep(1)
                # 펫 데이터 업데이트
                if self.pet_data_provider:
                    import json
                    data = json.dumps(self.pet_data_provider()).encode("utf-8")
                    self.server.get_characteristic(BLE_CHAR_PET_DATA_UUID).value = data

        except ImportError:
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": "bless 라이브러리가 설치되지 않았습니다. pip install bless"}
            })
        except Exception as e:
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": f"BLE 서버 시작 실패: {e}"}
            })

    def _on_read_pet_data(self, characteristic, **kwargs):
        """펫 데이터 읽기 요청 처리"""
        if self.pet_data_provider:
            import json
            return json.dumps(self.pet_data_provider()).encode("utf-8")
        return b"{}"

    def _on_write_message(self, characteristic, value, **kwargs):
        """메시지 수신 처리"""
        from network.protocol import Message
        msg = Message.from_bytes(value)
        if msg:
            self.message_queue.put({
                "type": "ble_message",
                "data": msg
            })

    def stop(self):
        """서버 중지"""
        self.advertising = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)

    def notify(self, message):
        """연결된 클라이언트에게 알림 전송"""
        if self.server and self.advertising:
            try:
                data = message.to_bytes()
                char = self.server.get_characteristic(BLE_CHAR_MESSAGE_UUID)
                if char:
                    char.value = data
                    self.server.update_value(BLE_SERVICE_UUID, BLE_CHAR_MESSAGE_UUID)
            except Exception as e:
                self.message_queue.put({
                    "type": "ble_error",
                    "data": {"error": f"알림 전송 실패: {e}"}
                })
