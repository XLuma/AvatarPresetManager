import socket
import threading
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

class OscQueryDiscovery():
    def __init__(self):
        """
        Initiates a new OscQueryDiscovery. On initialization, will attempt to discover a OSCQuery service running. Blocking.
        """
        print("Hello")
        self.zeroconf = Zeroconf()
        self.serviceBrowser = {}
        self.ip = ""
        self.port = ""
        self.name = ""
        self.host = ""
        self._found = threading.Event()
        self.serviceBrowser = ServiceBrowser(self.zeroconf, "_oscjson._tcp.local.", handlers=[self.scan])

        pass
    def scan(self, zeroconf: Zeroconf, service_type, name: str, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and name.lower().startswith("vrchat"):
                ips = self.inet_addrs(info.addresses)
                print("found vrchat")
                print(f"Name: {name}")
                print(f"Host: {info.server}")
                print(f"IP : {', '.join(ips)}")
                print(f"Port: {info.port}")
                self.ip = ips[0]
                self.port = info.port
                self.name = name
                self.host = info.server
                self._found.set()
                
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
        return self._found.wait(timeout=timeout)
    def stop(self):
        self.zeroconf.close()