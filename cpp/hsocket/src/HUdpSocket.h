﻿#pragma once
#include "HSocket.h"
#include "Message.h"

class HUdpSocket : public HSocket
{
	bool sendMsg(Message &msg, IPv4Address &addr);

	Message recvMsg(IPv4Address *addr);
};