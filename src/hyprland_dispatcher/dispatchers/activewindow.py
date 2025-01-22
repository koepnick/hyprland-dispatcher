from hyprland_dispatcher import listener, HyprlandEvent

@listener.dispatcher.register("activewindow")
def handle_active_window(event: HyprlandEvent):
    window_class, window_title = event.data.split(',', 1)
    print(f"Window focus changed to: {window_class} - {window_title}")
