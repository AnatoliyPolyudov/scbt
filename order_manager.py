from event_bus import subscribe

def handle_button_click(data):
    print("ORDER_MANAGER: Received button click:", data)
    
    action = data.get("action")
    price = data.get("price")
    
    if action == "BUY_LIMIT":
        print(f"TEST_ORDER: Would create BUY LIMIT at {price}")
    elif action == "SELL_LIMIT":
        print(f"TEST_ORDER: Would create SELL LIMIT at {price}")
    elif action == "BUY_MARKET":
        print("TEST_ORDER: Would create BUY MARKET (current price)")
    elif action == "SELL_MARKET":
        print("TEST_ORDER: Would create SELL MARKET (current price)")

subscribe("BUTTON_CLICK", handle_button_click)