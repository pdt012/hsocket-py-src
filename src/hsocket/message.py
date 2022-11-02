# -*- coding: utf-8 -*-
from typing import Optional, Any
import json


class ProtoCode:
    NONE = 0x0  # 空报文
    ERROR_ = 0x1  # 错误报文
    HEADERONLY = 0x2  # 只含报头
    PLAINTEXT = 0x3  # 纯文本内容
    JSONOBJRCT = 0x4  # JSON对象


class MessageConfig:
    ENCODING = "UTF-8"


class Header:
    HEADER_LENGTH = 8

    def __init__(self, protocode, opcode, statuscode, length):
        self.protocode: int = protocode
        self.opcode: int = opcode
        self.statuscode: int = statuscode
        self.length: int = length
    
    def to_bytes(self) -> bytes:
        header = b""
        header += self.protocode.to_bytes(1, 'little', signed=False)  # 协议码
        header += self.opcode.to_bytes(1, 'little', signed=False)  # 操作码
        header += self.statuscode.to_bytes(2, 'little', signed=False)  # 状态码
        header += self.length.to_bytes(4, 'little', signed=False)  # 报文长度
        return header

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional["Header"]:
        if len(data) != cls.HEADER_LENGTH:
            return None
        protocode = int(data[0])  # 协议码
        opcode = int(data[1])  # 操作码
        statuscode = int().from_bytes(data[2:4], 'little', signed=False)  # 响应码
        length = int().from_bytes(data[4:8], 'little', signed=False)  # 文本内容起始位置
        return Header(protocode, opcode, statuscode, length)


class Message:
    def __init__(self, protocode=ProtoCode.NONE, opcode=0, statuscode=0, content: str = ""):
        self.__protocode: int = protocode
        self.__opcode: int = opcode
        self.__statuscode: int = statuscode
        self.__content: str = ""
        self.__json: dict = {}
        
        if content:
            if protocode == ProtoCode.HEADERONLY:
                pass
            elif protocode == ProtoCode.PLAINTEXT:
                self.__content = content
            elif protocode == ProtoCode.JSONOBJRCT:
                self.__content = content
                self.__json = json.loads(content)
    
    @classmethod
    def HeaderContent(cls, header: Header, content: str) -> "Message":
        if header == None:
            return Message()
        msg = Message(header.protocode, header.opcode, header.statuscode, content)
        return msg

    @classmethod
    def HeaderOnlyMsg(cls, opcode=0, statuscode=0):
        msg = Message(ProtoCode.HEADERONLY, opcode, statuscode)
        return msg
        
    @classmethod
    def PlainTextMsg(cls, opcode=0, statuscode=0, text: str = ""):
        msg = Message(ProtoCode.PLAINTEXT, opcode, statuscode)
        msg.__content = text
        return msg
        
    @classmethod
    def JsonMsg(cls, opcode=0, statuscode=0, dict_: dict = None, **kw):
        msg = Message(ProtoCode.JSONOBJRCT, opcode, statuscode)
        if dict_ is not None:
            msg.__json = dict_
        for key in kw.keys():
            if kw[key] is not None:
                msg.__json[key] = kw[key]
        return msg

    def isValid(self):
        return self.__protocode != ProtoCode.NONE and self.__protocode != ProtoCode.ERROR_

    def get(self, key: str) -> Any:
        ret = self.__json.get(key)
        return ret

    def content(self) -> str:
        return self.__content

    def protocode(self) -> int:
        """获取协议码"""
        return self.__protocode
        
    def opcode(self) -> int:
        """获取操作码"""
        return self.__opcode

    def statuscode(self) -> int:
        """获取状态码"""
        return self.__statuscode
        
    def to_bytes(self) -> bytes:
        if self.__protocode == ProtoCode.HEADERONLY:
            content = b""
        elif self.__protocode == ProtoCode.PLAINTEXT:
            content = self.__content.encode(MessageConfig.ENCODING)
        elif self.__protocode == ProtoCode.JSONOBJRCT:
            content = json.dumps(self.__json).encode(MessageConfig.ENCODING)
        else:
            content = self.__content.encode(MessageConfig.ENCODING)
        length = len(content)  # 数据包长度(不包含报头)
        header = Header(self.__protocode, self.__opcode, self.__statuscode, length)
        return header.to_bytes() + content

    @classmethod
    def from_bytes(cls, data: bytes):
        if len(data) < Header.HEADER_LENGTH:
            return Message()
        header = Header.from_bytes(data[0:8])
        if header == None:
            return Message()
        msg = Message.HeaderContent(header, data[8:].decode(MessageConfig.ENCODING))
        return msg

    def __str__(self):
        return (f"pro:{self.__protocode}  op:{self.__opcode}  sta:{self.__statuscode}\n"
                f"content:\n{self.__content}")
    
    def __repr__(self):
        return str(self)
