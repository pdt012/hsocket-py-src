# HSocket

- 兼容c++和python的协议；
- 支持纯文本/json的数据报协议;
- 基于该协议的tcp/udp通信api
- 对tcp协议下文件传输的简单封装。

## python端
- 基于selectors实现的一对多tcp服务器类;
- udp服务器类;
- 支持同步(request-response模式)/异步(多线程收发)的tcp/udp客户端类。  

## c++端
- 对winSock的封装；
- 打包为lib供其他应用使用。
