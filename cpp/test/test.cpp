#include <iostream>
#include "../hsocket/include/HTcpSocket.h"

#ifdef _DEBUG
#pragma comment(lib,"../Debug/hsocket.lib")
#else
#pragma comment(lib,"..\\Release\\hsocket.lib")
#endif

int main()
{
	try {
		HTcpSocket socket = HTcpSocket();
		socket.connect("127.0.0.1", 40000);
		std::cout << "start" << std::endl;
		neb::CJsonObject json;
		json.Add("text0", "<0>test message send by c++ client");
		Message msg = Message::JsonMsg(0, 0, json);
		socket.sendMsg(msg);
		Message replyMsg = socket.recvMsg();
		if (replyMsg.isValid()) {
			std::cout << replyMsg.toString() << std::endl;
		}
	}
	catch (ConnectionError e) {
		std::cout << e.what() << std::endl;
		return 0;
	}
}
