#include "pch.h"
#include "HUdpSocket.h"

bool HUdpSocket::sendMsg(Message &msg, IPv4Address &addr)
{
	return sendto(msg.toString(), addr);
}

Message HUdpSocket::recvMsg(IPv4Address *addr)
{
	Message msg = Message::fromString(recvfrom(addr));
	return msg;
}
