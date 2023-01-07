#include <iostream>
#include "../hsocket/include/HTcpSocket.h"
#include "../hsocket/include/convert/convert.cpp"

#ifdef _DEBUG
#pragma comment(lib,"../Debug/hsocketd.lib")
#else
#pragma comment(lib,"..\\Release\\hsocket.lib")
#endif

int main()
{
	try {
		HTcpSocket socket = HTcpSocket();
		socket.connect("127.0.0.1", 40000);
		std::cout << "start" << std::endl;
		while (true) {
			int code = -1;
			std::cout << ">>>";
			std::cin >> code;
			if (std::cin.fail()) break;
			switch (code)
			{
			case 0: {
				neb::CJsonObject json;
				json.Add("text0", "<0>test message send by c++ client");
				Message msg = Message::JsonMsg(0, 0, json);
				socket.sendMsg(msg);
				Message replyMsg = socket.recvMsg();
				if (replyMsg.isValid()) {
					std::cout << replyMsg.toString() << std::endl;
				}}
				  break;
			case 100:
				socket.sendMsg(Message::HeaderOnlyMsg(100));
				socket.sendFile("testfile/test1.txt", "test1_by_cpp_client.txt");
				break;
			case 101:
				socket.sendMsg(Message::HeaderOnlyMsg(101));
				socket.recvFile();
				break;
			case 110: {
				socket.sendMsg(Message::HeaderOnlyMsg(110));
				std::vector<std::string> pathlist = { "testfile/test1.txt", "testfile/test2.txt" };
				std::vector<std::string> namelist = { "test1_by_cpp_client.txt", "test2_by_cpp_client.txt" };
				socket.sendFiles(pathlist, namelist); }
					break;
			case 111:
				socket.sendMsg(Message::HeaderOnlyMsg(111));
				socket.recvFiles();
				break;
			default:
				break;
			}

		}
	}
	catch (ConnectionError e) {
		std::cout << e.what() << std::endl;
		return 0;
	}
}
