"""
BLE 통신 모듈 - Central (스캔/연결) 역할
Bleak 라이브러리 사용
"""
import asyncio
import threading
import queue
import time
from data.constants import BLE_SERVICE_UUID, BLE_CHAR_PET_DATA_UUID, BLE_CHAR_MESSAGE_UUID


class BLECentral:
    """BLE Central - 주변 펫 스캔 및 연결"""

    def __init__(self, message_queue=None):
        self.message_queue = message_queue or queue.Queue()
        self.connected = False
        self.scanning = False
        self.found_devices = []
        self.client = None
        self._loop = None
        self._thread = None

    def start(self):
        """별도 스레드에서 asyncio 이벤트 루프 시작"""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        """비동기 이벤트 루프 실행"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def stop(self):
        """정리"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)
        self.connected = False

    def scan(self, duration=5.0):
        """BLE 기기 스캔 시작"""
        if not self._loop:
            self.start()

        asyncio.run_coroutine_threadsafe(
            self._async_scan(duration), self._loop
        )

    async def _async_scan(self, duration):
        """비동기 스캔"""
        try:
            from bleak import BleakScanner

            self.scanning = True
            self.found_devices = []

            self.message_queue.put({
                "type": "ble_scan_start",
                "data": {}
            })

            devices = await BleakScanner.discover(timeout=duration)

            for d in devices:
                device_info = {
                    "name": d.name or "Unknown",
                    "address": d.address,
                    "rssi": d.rssi if hasattr(d, 'rssi') else -100,
                }
                self.found_devices.append(device_info)

                # 다마고치 서비스 필터링
                # (실제로는 서비스 UUID로 필터링해야 함)
                self.message_queue.put({
                    "type": "ble_device_found",
                    "data": device_info
                })

            self.scanning = False
            self.message_queue.put({
                "type": "ble_scan_done",
                "data": {"count": len(self.found_devices)}
            })

        except ImportError:
            self.scanning = False
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": "bleak 라이브러리가 설치되지 않았습니다. pip install bleak"}
            })
        except Exception as e:
            self.scanning = False
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": str(e)}
            })

    def connect(self, address):
        """특정 기기에 연결"""
        if not self._loop:
            self.start()

        asyncio.run_coroutine_threadsafe(
            self._async_connect(address), self._loop
        )

    async def _async_connect(self, address):
        """비동기 연결"""
        try:
            from bleak import BleakClient

            self.client = BleakClient(address)
            await self.client.connect()
            self.connected = True

            self.message_queue.put({
                "type": "ble_connected",
                "data": {"address": address}
            })

            # 서비스/캐릭터리스틱 탐색
            services = self.client.services
            for service in services:
                if service.uuid == BLE_SERVICE_UUID:
                    # 알림 구독
                    for char in service.characteristics:
                        if char.uuid == BLE_CHAR_MESSAGE_UUID:
                            await self.client.start_notify(
                                char.uuid, self._on_notification
                            )

        except ImportError:
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": "bleak 라이브러리가 설치되지 않았습니다."}
            })
        except Exception as e:
            self.connected = False
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": f"연결 실패: {e}"}
            })

    def _on_notification(self, sender, data):
        """BLE 알림 수신"""
        from network.protocol import Message
        msg = Message.from_bytes(data)
        if msg:
            self.message_queue.put({
                "type": "ble_message",
                "data": msg
            })

    def send(self, message):
        """메시지 전송"""
        if not self.connected or not self.client:
            return False

        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._async_send(message), self._loop
            )
            return True
        return False

    async def _async_send(self, message):
        """비동기 메시지 전송"""
        try:
            data = message.to_bytes()
            await self.client.write_gatt_char(
                BLE_CHAR_MESSAGE_UUID, data
            )
        except Exception as e:
            self.message_queue.put({
                "type": "ble_error",
                "data": {"error": f"전송 실패: {e}"}
            })

    def disconnect(self):
        """연결 해제"""
        if self.client and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._async_disconnect(), self._loop
            )

    async def _async_disconnect(self):
        try:
            if self.client and self.client.is_connected:
                await self.client.disconnect()
            self.connected = False
            self.message_queue.put({
                "type": "ble_disconnected",
                "data": {}
            })
        except Exception:
            pass
