#-*- coding: utf8 -*-

import time
import json
import sys
import logging
import os
import os.path
import inspect
import copy
from functools import wraps
from ctypes import WinDLL,c_ulong,c_char_p,create_string_buffer,WINFUNCTYPE

import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger('WxWorkManager')

def is_64bit():
    return sys.maxsize > 2**32

def c_string(data):
    return c_char_p(data.encode('utf-8'))

class MessageType:
    MT_APP_READY_MSG = 11024
    MT_PARAMS_ERROR_MSG = 11025
    MT_USER_LOGIN = 11026
    MT_USER_LOGOUT = 11027
    MT_LOGIN_QRCODE_MSG = 11028
    MT_SEND_TEXT_MSG = 11029
    MT_SEND_IMAGE_MSG = 11030
    MT_SEND_FILE_MSG = 11031
    MT_SEND_LINK_MSG = 11033
    MT_SEND_VIDEO_MSG = 11067
    MT_SEND_PERSON_CARD_MSG = 11034
    MT_RECV_TEXT_MSG = 11041
    MT_RECV_IMG_MSG = 11042
    MT_RECV_VIDEO_MSG = 11043
    MT_RECV_VOICE_MSG = 11044
    MT_RECV_FILE_MSG = 11045
    MT_RECV_LOCATION_MSG = 11046
    MT_RECV_LINK_CARD_MSG = 11047
    MT_RECV_EMOTION_MSG = 11048	
    MT_RECV_RED_PACKET_MSG = 11049
    MT_RECV_PERSON_CARD_MSG = 11050	
    MT_RECV_OTHER_MSG = 11051

class CallbackHandler:
    pass

_GLOBAL_CONNECT_CALLBACK_LIST = []
_GLOBAL_RECV_CALLBACK_LIST = []
_GLOBAL_CLOSE_CALLBACK_LIST = []


def CONNECT_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        f._wx_connect_handled = True
        if not in_class:
            _GLOBAL_CONNECT_CALLBACK_LIST.append(f)
        return f
    return decorator

def RECV_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        f._wx_recv_handled = True
        if not in_class:
            _GLOBAL_RECV_CALLBACK_LIST.append(f)  
        return f         
    return decorator

def CLOSE_CALLBACK(in_class=False):
    def decorator(f):
        wraps(f)
        f._wx_close_handled = True
        if not in_class:
            _GLOBAL_CLOSE_CALLBACK_LIST.append(f)  
        return f         
    return decorator  

def add_callback_handler(callbackHandler):
    for dummy, handler in inspect.getmembers(callbackHandler, callable): 
        if hasattr(handler, '_wx_connect_handled'):          
            _GLOBAL_CONNECT_CALLBACK_LIST.append(handler)
        elif hasattr(handler, '_wx_recv_handled'):
            _GLOBAL_RECV_CALLBACK_LIST.append(handler)
        elif hasattr(handler, '_wx_close_handled'):
            _GLOBAL_CLOSE_CALLBACK_LIST.append(handler)

@WINFUNCTYPE(None, c_ulong)
def wxwork_connect_callback(client_id):
    for func in _GLOBAL_CONNECT_CALLBACK_LIST:
        func(client_id)


@WINFUNCTYPE(None, c_ulong, c_char_p, c_ulong)
def wxwork_recv_callback(client_id, data, length):
    data = copy.deepcopy(data)
    json_data = data.decode('utf-8')
    dict_data  = json.loads(json_data)
    for func in _GLOBAL_RECV_CALLBACK_LIST:
        func(client_id, dict_data['type'], dict_data['data'])

@WINFUNCTYPE(None, c_ulong)
def wxwork_close_callback(client_id):
    for func in _GLOBAL_CLOSE_CALLBACK_LIST:
        func(client_id)


class REQUIRE_WXLOADER:   
    def __init__(self, func):
        self.func = func
        
    def __get__(self, obj, cls):    
        def wrapper(*args, **kwargs):
            if obj.WXLOADER is not None:
                return self.func(obj, *args, **kwargs)
            else:
                logger.error("WxWorkApi未初始化或初始化失败")
        return wrapper


class WxWorkManager:
    
    # 加载器
    WXLOADER = None
    
    # WxWorkHelper.dll
    wxhelper_dll_path = ''

    # 可指定WXWork.exe路径，也可以设置为空
    wxwork_exe_path = ''

    def __init__(self, libs_path, wxwork_exe_path=''):
        self.wxwork_exe_path = wxwork_exe_path
        wxwork_loader_path = os.path.join(libs_path, 'WxWorkLoader_{0}.dll'.format('x64' if is_64bit() else 'x86'))
        wxwork_loader_path = os.path.realpath(wxwork_loader_path)

        if not os.path.exists(wxwork_loader_path):
            logger.error('libs目录错误，或dll文件不存在')
            return  

        self.WXLOADER = WinDLL(wxwork_loader_path)  
        
        # 使用utf8编码
        self.WXLOADER.UseUtf8()

        # 初始化接口回调
        self.WXLOADER.InitWxWorkSocket(wxwork_connect_callback, wxwork_recv_callback, wxwork_close_callback)

        self.wxhelper_dll_path = '{0}/WxWorkHelper_{1}.dll'.format(libs_path, self.get_user_wxwork_version())
        if not os.path.exists(self.wxhelper_dll_path):
            logger.error('lib文件：%s不存在', self.wxhelper_dll_path);
            return
            
        if  wxwork_exe_path != '' and not os.path.exists(wxwork_exe_path):
            logger.warning('WXWork.exe路径是否设置正确?')

        self.wxwork_exe_path = wxwork_exe_path

    def add_callback_handler(self, callback_handler):
        add_callback_handler(callback_handler)
          
    @REQUIRE_WXLOADER
    def get_user_wxwork_version(self):
        out = create_string_buffer(20)
        self.WXLOADER.GetUserWxWorkVersion(out)
        return out.value.decode('utf-8')
    
    @REQUIRE_WXLOADER
    def manager_wxwork(self, smart=True):
        if smart:
            return self.WXLOADER.InjectWxWork(c_string(self.wxhelper_dll_path), c_string(self.wxwork_exe_path))
        else:
            return self.WXLOADER.InjectWxWorkMultiOpen(c_string(self.wxhelper_dll_path), c_string(self.wxwork_exe_path))
    
    @REQUIRE_WXLOADER
    def manager_wxwork_by_pid(self, wxwork_pid):
        return self.WXLOADER.InjectWxWorkPid(wxwork_pid, c_string(self.wxhelper_dll_path))

    @REQUIRE_WXLOADER
    def close_manager():
        return self.WXLOADER.DestroyWxWork()

    @REQUIRE_WXLOADER
    def send_message(self, client_id, message_type, params):
        send_data = {
            'type': message_type,
            'data': params
        }
        return self.WXLOADER.SendWxWorkData(client_id, c_string(json.dumps(send_data)))

    def send_text(self, client_id, conversation_id, text):
        data = {
            'conversation_id': conversation_id,
            'content': text
        }
        return self.send_message(client_id, MessageType.MT_SEND_TEXT_MSG, data)

    def send_image(self, client_id, conversation_id, image_path):
        data = {
            'conversation_id': conversation_id,
            'file': image_path
        }
        return self.send_message(client_id, MessageType.MT_SEND_IMAGE_MSG, data)


    def send_file(self, client_id, conversation_id, file):
        data = {
            'conversation_id': conversation_id,
            'file': file
        }
        return self.send_message(client_id, MessageType.MT_SEND_FILE_MSG, data)

    def send_link(self, client_id, conversation_id, title, desc, url, image_url):
        data = {
            'conversation_id': conversation_id,
            'title': title,
            'desc': desc,
            'url': url,
            'image_url': image_url
        }
        return self.send_message(client_id, MessageType.MT_SEND_LINK_MSG, data)

    def send_video(self, client_id, conversation_id, video_path):
        data = {
            'conversation_id': conversation_id,
            'file': video_path
        }
        return self.send_message(client_id, MessageType.MT_SEND_VIDEO_MSG, data)

