import socket
import threading
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

class OscQueryDiscovery():
    def __init__(self):
        """
        Initiates a new OscQueryDiscovery.
        """
        self.__zeroconf = Zeroconf()
        self.ip = ""
        self.port: int = 0
        self.name = ""
        self.host = ""
        self.__found = threading.Event()
        self.__serviceBrowser = ServiceBrowser(self.__zeroconf, "_oscjson._tcp.local.", handlers=[self.scan])
        pass
    def scan(self, zeroconf: Zeroconf, service_type, name: str, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and name.lower().startswith("vrchat"):
                ips = self.inet_addrs(info.addresses)
                self.ip = ips[0]
                self.port = info.port
                self.name = name
                self.host = info.server
                self.__found.set()
        pass
    def inet_addrs(self, addresses):
        out = []
        for addr in addresses:
            try:
                out.append(socket.inet_ntop(socket.AF_INET, addr))
            except OSError:
                pass
        return out
    def wait(self, timeout):
        return self.__found.wait(timeout=timeout)
    def stop(self):
        self.__zeroconf.close()