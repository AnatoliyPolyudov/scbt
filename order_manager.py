from event_bus import subscribe
from exchange import place_order

def handle_button_click(data):
    print("ORDER_MANAGER: Received button click:", data)
    
    action = data.get("action")
    price = float(data.get("price"))

    if action == "BUY_LIMIT":
        print(f"Placing BUY LIMIT at {price}")
        place_order("BUY", price)
    elif action == "SELL_LIMIT":
        print(f"Placing SELL LIMIT at {price}")
        place_order("SELL", price)

subscribe("BUTTON_CLICK", handle_button_click)
