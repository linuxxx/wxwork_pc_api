# Python调用介绍

实际上对[dll接口](dll.md)进行封装， 具体的json参数可以看[API文档](api.md)

# 快速上手

```python
import wxwork
import json
import time
from wxwork import WxWorkManager,MessageType

wxwork_manager = WxWorkManager(libs_path='../../libs')

# 这里测试函数回调
@wxwork.CONNECT_CALLBACK(in_class=False)
def on_connect(client_id):
    print('[on_connect] client_id: {0}'.format(client_id))

@wxwork.RECV_CALLBACK(in_class=False)
def on_recv(client_id, message_type, message_data):
    print('[on_recv] client_id: {0}, message_type: {1}, message:{2}'.format(client_id, 
    message_type, json.dumps(message_data)))

@wxwork.CLOSE_CALLBACK(in_class=False)
def on_close(client_id):
    print('[on_close] client_id: {0}'.format(client_id))

if __name__ == "__main__":
    wxwork_manager.manager_wxwork(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5)
```

# 启动企业微信接口

- 获取用户电脑上安装的企业微信版本号： wxwork_manager.get_user_wxwork_version
- 智能管理（启动/多开）企业微信程序： wxwork_manager.manager_wxwork
- 通过进程号管理企业微信： wxwork_manager.manager_wxwork_by_pid
- 释放所有： wxwork_manager.close_manager

# 发送接口

- 发送文本消息： wxwork_manager.send_text 
- 发送图片消息： wxwork_manager.send_image
- 发送文件消息： wxwork_manager.send_file
- 发送链接消息： wxwork_manager.send_link
- 发送视频消息： wxwork_manager.send_video




