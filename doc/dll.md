# DLL介绍

dll文件有三个，分别是WxWorkHelper_3.0.14.1205.dll、WxWorkLoader_x86.dll和WxWorkLoader_x64.dll

# WxWorkHelper.dll

客户端程序，用于在企业微信程序内部与外界通信，用于接收指令和消息通知

# WxWorkLoader.dll

管理端程序，支持32位（WxWorkLoader_x86.dll）和64位（WxWorkLoader_x64.dll）调用， 用于智能管理企业微信，如管理已经打开的企业微信进程，多开企业微信。

提供的接口如下：
1. GetUserWxWorkVersion

	获取当前用户的电脑上安装的企业微信版本，如： 3.0.0.1001

	函数定义：

	```BOOL GetUserWxWorkVersion(OUT LPSTR szVersion)```

	传一个ANSI字符串缓冲区的指针，长度30即可， 这个函数可以先获取当前用户电脑上安装的微信版本，然后判断我们的dll是否支持，如果不支持就提示用户下载我们支持的版本。

2. UseUtf8
	
    在所有接口前执行，执行后接口全部使用utf8编码传输

	函数定义:
	
    ```BOOL UseUtf8()```
	
	
3. InitWxWorkSocket

	用于socket的回调处理

	函数定义：

	```BOOL InitWxWorkSocket(IN DWORD dwConnectCallback, IN DWORD dwRecvCallback, IN DWORD dwCloseCallback)```

	其中dwConnectCallback是一个函数指针类型, 在有新客户端加入时调用，结构如下：

		```void  MyConnectCallback(int iClientId)```

        传入的一个参数是socket的客户ID,返回值为空 

	dwRecvCallback是一个函数指针类型,在接收到新消息时调用，结构如下：

		```void  MyRecvCallback(int iClientId, char* szJsonData, int iLen)```

	dwCloseCallback是一个函数指针类型，在客户端退出时调用，结果如下:

		```void  MyCloseCallback(int iClientId)```
	
4. InjectWxWork

	用于智能多开，并注入dll, 参数1：WxWorkHelper.dll路径，参数2：WXWork.exe路径，可传空，会读取企业微信安装目录， 注入成功返回企业微信的进程ID, 失败返回0
	
    函数定义：
	
    ```DWORD  InjectWxWork(IN LPCSTR szDllPath，IN LPCSTR szWxWorkExePath)```


	如果需要一个软件，管理多个企业微信，多次调用这个函数实现，通过socket回调管理客户端

5. InjectWxWorkPid
	注入指定的企业微信进程，参数1： WXWork.exe进程id, 参数2： dll路径

	函数定义：
	
    ```DWORD InjectWxWorkPid(IN DWORD dwPid, IN LPCSTR szDllPath)```
	
6. InjectWxWorkMultiOpen

	多开一个新的企业微信并注入，不维护已经打开的企业微信，需要两个参数，参数1：WxWorkHelper.dll的路径，参数2：指定要启动企业微信（WxWork.exe）的完整路径，如果不提供，可以设置0或空字符串，将自动读取企业微信的安装目录

	函数定义：

	```DWORD __stdcall InjectWxWorkMultiOpen(IN LPCSTR szDllPath, IN LPCSTR szWxWorkExePath)```

	
7. SendWxWorkData

	用于向企业微信发送指令，指令内容参考功能类。
	
    函数定义：

	```BOOL  SendWxWorkData(IN CONNID dwClientId, IN LPCSTR szJsonData)```
	
8. DestroyWxWork

	主程序退出前，执行释放函数，用于卸载DLL和关闭socket服务端

	函数定义：

	```BOOL  DestroyWxWork()```
	
    
