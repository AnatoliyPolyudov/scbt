from event_bus import subscribe

def handle_button_click(data):
    print("ORDER_MANAGER: Received button click:", data)
    
    action = data.get("action")
    price = data.get("price")
    
    if action == "BUY_LIMIT":
        print(f"TEST_ORDER: Would create BUY LIMIT at {price}")
    elif action == "SELL_LIMIT":
        print(f"TEST_ORDER: Would create SELL LIMIT at {price}")

subscribe("BUTTON_CLICK", handle_button_click)
