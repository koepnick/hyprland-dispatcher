from hyprland_dispatcher import HyprlandEventListener

# Create a global listener instance that dispatchers can import
listener = HyprlandEventListener()

if __name__ == "__main__":
    # Start listening for events
    listener.start()
