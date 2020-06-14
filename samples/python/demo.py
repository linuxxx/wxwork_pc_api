#-*- coding: utf8 -*-

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


class EchoBot(wxwork.CallbackHandler):


    @wxwork.RECV_CALLBACK(in_class=True)
    def on_message(self, client_id, message_type, message_data):

        # 如果是文本消息，就回复一条消息
        if message_type == MessageType.MT_RECV_TEXT_MSG:
            reply_content = u'😂😂😂你发过来的消息是：{0}'.format(message_data['content'])
            time.sleep(2)
            wxwork_manager.send_text(client_id, message_data['conversation_id'], reply_content)


if __name__ == "__main__":
    echoBot = EchoBot()

    # 添加回调实例对象
    wxwork_manager.add_callback_handler(echoBot)
    wxwork_manager.manager_wxwork(smart=True)

    # 阻塞主线程
    while True:
        time.sleep(0.5)
