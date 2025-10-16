from event_bus import subscribe

def handle_button_click(data):
    print("ORDER_MANAGER: Received button click:", data)

subscribe("BUTTON_CLICK", handle_button_click)