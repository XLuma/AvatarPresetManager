import json
import logging
import re
import socket
from typing import Any


class xsoverlay_content:
    def __init__(self, title: str, sourceApp: str, timeout: int = 5, audioPath: str = "", content: str = "",  icon: str = "", **kwargs):
        """XSOverlay Content
        Args:
            title (str): Notification title, supports Rich Text Formatting
            sourceApp (str): Somewhere to put your app name for debugging purposes
            timeout (int, optional): How long the notification will stay on screen for in seconds. Defaults to 5.
            audioPath (str, optional): File path to .ogg audio file. Can be "default", "error", or "warning". Notification will be silent if left empty. Defaults to empty.
            content (str, optional):  Notification content, supports Rich Text Formatting, if left empty, notification will be small. Defaults to empty.
            icon (str, optional): Base64 Encoded image, or file path to image. Can also be "default", "error", or "warning". Defaults to empty.
        """
       
        self.title = title
        self.sourceApp = sourceApp
        self.timeout = timeout
        self.content = content
        self.audioPath = audioPath       
        self.useBase64Icon = b64checker(icon)
        self.icon = icon

        self.messageType = kwargs.get("attr", 1)         # 1 = Notification Popup, 2 = MediaPlayer Information, will be extended later on.
        self.height =  kwargs.get("attr", 175)           # Height notification will expand to if it has content other than a title.
        self.index =  kwargs.get("attr", 0)              # Only used for Media Player, changes the icon on the wrist.
        self.opacity =  kwargs.get("attr", 1)            # Opacity of the notification, to make it less intrusive. Setting to 0 will set to 1.
        self.volume =  kwargs.get("attr", float(0.7))    # Notification sound volume.
        

def b64checker(data: Any) -> bool:
    if not isinstance(data, str): return False
    return bool(re.search("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$", data))
    

def send_to_socket(content: dict, port: int = 42069):
    # * "XSOverlay ONLY listens for messages from localhost. You CANNOT currently send messages over the network to a different machine."
    iptup = ("127.0.0.1", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #logging.debug("Socket created")
 
    json_string = json.dumps(vars(content), ensure_ascii=False).encode('utf8')
    s.sendto(json_string, iptup)
