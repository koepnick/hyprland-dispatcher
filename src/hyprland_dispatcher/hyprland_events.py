import os
import socket
from typing import Callable, Dict
from dataclasses import dataclass
import importlib
import pkgutil
from pathlib import Path

@dataclass
class HyprlandEvent:
    type: str
    data: str

class HyprlandEventDispatcher:
    def __init__(self):
        self.handlers: Dict[str, list[Callable[[HyprlandEvent], None]]] = {}
        
    def register(self, event_type: str) -> Callable:
        def decorator(func: Callable[[HyprlandEvent], None]):
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(func)
            return func
        return decorator
    
    def dispatch(self, event: HyprlandEvent) -> None:
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

class HyprlandEventListener:
    socket_base = "/var/run/user/1000/hypr/"
    def __init__(self):
        self.dispatcher = HyprlandEventDispatcher()
        self._load_dispatchers()
    
    def get_socket_path(self) -> str:
        signature = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
        if not signature:
            raise Exception("Not running under Hyprland")
        return os.path.join(self.socket_base, signature, ".socket2.sock")

    def _load_dispatchers(self):
        """Dynamically load all dispatchers from the dispatchers directory"""
        dispatchers_path = Path(__file__).parent / 'dispatchers'
        if not dispatchers_path.exists():
            print("No dispatchers found")
            return

        # Import all modules in the dispatchers directory
        for module_info in pkgutil.iter_modules([str(dispatchers_path)]):
            print(module_info)
            if not module_info.name.startswith('_'):  # Skip __init__.py
                importlib.import_module(f'hyprland_dispatcher.dispatchers.{module_info.name}')
    
    def start(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print(f"Connecting to: {self.get_socket_path()}")
        sock.connect(self.get_socket_path())
        
        while True:
            try:
                msg = sock.recv(4096).decode("utf-8")
                messages = msg.strip().split('\n')
                
                for message in messages:
                    if '>>' not in message:
                        continue
                    
                    event_type, event_data = message.split(">>")
                    event = HyprlandEvent(event_type, event_data)
                    self.dispatcher.dispatch(event)
                    
            except Exception as e:
                print(f"Error handling event: {e}")
