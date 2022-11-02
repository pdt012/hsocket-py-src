# -*- coding: utf-8 -*-
from typing import Optional
import threading
from abc import abstractmethod
from .socket import HSocketTcp, HSocketUdp, ClientTcpSocket, ClientUdpSocket
from .message import Header, Message


class HSynTcpClient:
    """
    TCP / Synchronous Mode: 
    The client send a request and get the response in the same thread.
    """
    def __init__(self, addr):
        self.server_addr = addr
        self.__tcp_socket: "HSocketTcp" = ClientTcpSocket()
        self.__tcp_socket.setblocking(True)

    def settimeout(self, timeout):
        self.__tcp_socket.settimeout(timeout)

    def connect(self):
        self.__tcp_socket.connect(self.server_addr)

    def close(self):
        self.__tcp_socket.close()

    def isclosed(self) -> bool:
        return self.__tcp_socket.fileno() == -1

    def send(self, msg: "Message") -> bool:
        try:
            return self.__tcp_socket.sendMsg(msg)
        except ConnectionResetError:
            print("connection reset")
            self._onDisconnected()
            self.close()
            return False

    def request(self, msg: "Message") -> Optional["Message"]:
        if (self.send(msg)):
            try:
                response = self.__tcp_socket.recvMsg()
            except TimeoutError:
                return None
            except ConnectionResetError:
                print("connection reset")
                self._onDisconnected()
                self.close()
                return None
            else:
                return response
        return None

    def _onDisconnected(self):
        pass


class HAsynTcpClient:
    """
    TCP / Asynchronous Mode: 
    The client send and receive in two threads.
    """
    def __init__(self, addr):
        self.server_addr = addr
        self.__tcp_socket: "HSocketTcp" = ClientTcpSocket()
        self.__tcp_socket.setblocking(True)
        self.__running = False
        self.__message_thread = threading.Thread(target=self.__run, daemon=True)

    def connect(self):
        self.__tcp_socket.connect(self.server_addr)
        self.__running = True
        self.__message_thread.start()

    def close(self):
        self.__running = False
        self.__tcp_socket.close()

    def isclosed(self) -> bool:
        return self.__tcp_socket.fileno() == -1

    def send(self, msg: "Message") -> bool:
        try:
            return self.__tcp_socket.sendMsg(msg)
        except ConnectionResetError:
            self.__message_thread.join()  # make sure that '_onDisconnected' only run once
            if (not self.isclosed()):
                print("connection reset")
                self._onDisconnected()
                self.close()
            return False

    def __run(self):
        self.c=0
        while self.__running and not self.isclosed():
            try:
                msg = self.__tcp_socket.recvMsg()
            except TimeoutError:
                continue
            except ConnectionResetError:
                print("connection reset")
                self._onDisconnected()
                self.close()
                break
            else:
                self._messageHandle(msg)

    @abstractmethod
    def _messageHandle(self, msg: "Message"):
        ...

    def _onDisconnected(self):
        pass


class HSynUdpClient:
    """
    UDP / Synchronous Mode: 
    The client send a request and get the response in the same thread.
    """
    def __init__(self, addr):
        self.server_addr = addr
        self.__udp_socket: "HSocketUdp" = ClientUdpSocket()
        self.__udp_socket.setblocking(True)

    def settimeout(self, timeout):
        self.__udp_socket.settimeout(timeout)

    def close(self):
        self.__udp_socket.close()

    def request(self, msg: "Message") -> Optional["Message"]:
        try:
            self.__udp_socket.sendMsg(msg, self.server_addr)
            response, addr = self.__udp_socket.recvMsg()
        except TimeoutError:
            return None
        else:
            return response


class HAsynUdpClient:
    """
    UDP / Asynchronous Mode: 
    The client send and receive in two threads.
    """
    def __init__(self, addr):
        self.server_addr = addr
        self.__udp_socket: "HSocketUdp" = ClientUdpSocket()
        self.__udp_socket.setblocking(True)
        self.__running = False
        self.__message_thread = threading.Thread(target=self.__run, daemon=True)

    def close(self):
        self.__running = False
        self.__udp_socket.close()

    def isclosed(self) -> bool:
        return self.__udp_socket.fileno() == -1

    def send(self, msg: "Message") -> bool:
        ret = self.__udp_socket.sendMsg(msg, self.server_addr)
        # recvMsg before sendMsg will cause WinError10022.
        # So start the message thread after the first call of send.
        if not self.__running:
            self.__running = True
            self.__message_thread.start()
        return ret

    def __run(self):
        while self.__running:
            try:
                msg, addr = self.__udp_socket.recvMsg()
                # if (addr != self.server_addr):
                #     continue
            except TimeoutError:
                continue
            else:
                self._messageHandle(msg)

    @abstractmethod
    def _messageHandle(self, msg: "Message"):
        ...
