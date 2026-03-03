"""
WiFi 소켓 통신 모듈 (TCP)
BLE가 불가능할 때의 fallback
같은 네트워크 내에서 TCP 소켓으로 통신
"""
import asyncio
import threading
import queue
import socket
import json
import time
from data.constants import WIFI_DEFAULT_PORT, WIFI_BROADCAST_PORT, WIFI_DISCOVERY_MSG


class WiFiServer:
    """TCP 서버 - 연결 대기"""

    def __init__(self, port=WIFI_DEFAULT_PORT, message_queue=None):
        self.port = port
        self.message_queue = message_queue or queue.Queue()
        self.running = False
        self.clients = []
        self._thread = None
        self._server_socket = None

    def start(self):
        """서버 시작"""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()

    def _run_server(self):
        """서버 메인 루프"""
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", self.port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
            self.running = True

            local_ip = self._get_local_ip()
            self.message_queue.put({
                "type": "wifi_server_started",
                "data": {"ip": local_ip, "port": self.port}
            })

            while self.running:
                try:
                    client_sock, addr = self._server_socket.accept()
                    self.clients.append(client_sock)
                    self.message_queue.put({
                        "type": "wifi_client_connected",
                        "data": {"address": f"{addr[0]}:{addr[1]}"}
                    })

                    # 클라이언트별 수신 스레드
                    recv_thread = threading.Thread(
                        target=self._receive_from_client,
                        args=(client_sock, addr),
                        daemon=True
                    )
                    recv_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.message_queue.put({
                            "type": "wifi_error",
                            "data": {"error": f"서버 오류: {e}"}
                        })

        except Exception as e:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"서버 시작 실패: {e}"}
            })
        finally:
            self.running = False

    def _receive_from_client(self, client_sock, addr):
        """클라이언트로부터 메시지 수신"""
        try:
            client_sock.settimeout(1.0)
            buffer = b""

            while self.running:
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break

                    buffer += data

                    # 메시지 파싱 (길이 헤더 프로토콜)
                    while len(buffer) >= 4:
                        msg_len = int.from_bytes(buffer[:4], "big")
                        if len(buffer) < 4 + msg_len:
                            break

                        msg_data = buffer[4:4 + msg_len]
                        buffer = buffer[4 + msg_len:]

                        from network.protocol import Message
                        msg = Message.from_bytes(msg_data)
                        if msg:
                            self.message_queue.put({
                                "type": "wifi_message",
                                "data": msg,
                                "from": f"{addr[0]}:{addr[1]}"
                            })

                except socket.timeout:
                    continue

        except Exception as e:
            pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass
            if client_sock in self.clients:
                self.clients.remove(client_sock)
            self.message_queue.put({
                "type": "wifi_client_disconnected",
                "data": {"address": f"{addr[0]}:{addr[1]}"}
            })

    def broadcast(self, message):
        """모든 연결된 클라이언트에게 메시지 전송"""
        data = message.to_bytes()
        dead_clients = []
        for client in self.clients:
            try:
                client.sendall(data)
            except Exception:
                dead_clients.append(client)

        for c in dead_clients:
            try:
                c.close()
            except Exception:
                pass
            self.clients.remove(c)

    def stop(self):
        """서버 중지"""
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except Exception:
                pass
        self.clients.clear()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass

    def _get_local_ip(self):
        """로컬 IP 주소 가져오기"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


class WiFiClient:
    """TCP 클라이언트 - 서버에 연결"""

    def __init__(self, message_queue=None):
        self.message_queue = message_queue or queue.Queue()
        self.connected = False
        self.socket = None
        self._thread = None

    def connect(self, host, port=WIFI_DEFAULT_PORT):
        """서버에 연결"""
        self._thread = threading.Thread(
            target=self._connect_and_receive,
            args=(host, port),
            daemon=True
        )
        self._thread.start()

    def _connect_and_receive(self, host, port):
        """연결 및 수신 루프"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((host, port))
            self.socket.settimeout(1.0)
            self.connected = True

            self.message_queue.put({
                "type": "wifi_connected",
                "data": {"host": host, "port": port}
            })

            buffer = b""
            while self.connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break

                    buffer += data

                    while len(buffer) >= 4:
                        msg_len = int.from_bytes(buffer[:4], "big")
                        if len(buffer) < 4 + msg_len:
                            break

                        msg_data = buffer[4:4 + msg_len]
                        buffer = buffer[4 + msg_len:]

                        from network.protocol import Message
                        msg = Message.from_bytes(msg_data)
                        if msg:
                            self.message_queue.put({
                                "type": "wifi_message",
                                "data": msg,
                            })

                except socket.timeout:
                    continue

        except ConnectionRefusedError:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"연결 거부: {host}:{port}에 서버가 없습니다."}
            })
        except socket.timeout:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"연결 시간 초과: {host}:{port}"}
            })
        except Exception as e:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"연결 실패: {e}"}
            })
        finally:
            self.connected = False
            self.message_queue.put({
                "type": "wifi_disconnected",
                "data": {}
            })

    def send(self, message):
        """메시지 전송"""
        if not self.connected or not self.socket:
            return False
        try:
            data = message.to_bytes()
            self.socket.sendall(data)
            return True
        except Exception as e:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"전송 실패: {e}"}
            })
            return False

    def disconnect(self):
        """연결 해제"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass


class WiFiDiscovery:
    """UDP 브로드캐스트로 같은 네트워크 내 다마고치 검색"""

    def __init__(self, port=WIFI_BROADCAST_PORT, message_queue=None):
        self.port = port
        self.message_queue = message_queue or queue.Queue()
        self.running = False
        self._thread = None

    def start_listening(self):
        """브로드캐스트 수신 시작"""
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self):
        """브로드캐스트 수신"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", self.port))
            sock.settimeout(1.0)
            self.running = True

            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    msg = data.decode("utf-8")
                    if msg.startswith(WIFI_DISCOVERY_MSG):
                        # 뒤에 JSON으로 펫 정보가 있음
                        try:
                            info = json.loads(msg[len(WIFI_DISCOVERY_MSG):])
                            self.message_queue.put({
                                "type": "wifi_peer_found",
                                "data": {"ip": addr[0], "port": info.get("port", WIFI_DEFAULT_PORT),
                                         "pet_info": info.get("pet", {})}
                            })
                        except json.JSONDecodeError:
                            pass
                except socket.timeout:
                    continue

        except Exception as e:
            self.message_queue.put({
                "type": "wifi_error",
                "data": {"error": f"검색 오류: {e}"}
            })
        finally:
            self.running = False

    def broadcast(self, pet_info, port=WIFI_DEFAULT_PORT):
        """브로드캐스트로 자기 존재 알림"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            payload = WIFI_DISCOVERY_MSG + json.dumps({
                "port": port,
                "pet": pet_info,
            }, ensure_ascii=False)

            sock.sendto(payload.encode("utf-8"), ("<broadcast>", self.port))
            sock.close()
        except Exception:
            pass

    def stop(self):
        self.running = False
