# callback_handler.py
from event_bus import publish

def handle_callback(query_data):
    print("CALLBACK_HANDLER: Received callback:", query_data)
    
    if ':' in query_data:
        # Лимитные ордера с ценой: BUY_LIMIT:3800.50 или SELL_LIMIT:3800.50
        action, price = query_data.split(':')
        publish("BUTTON_CLICK", {"action": action, "price": price})
    else:
        # Кнопка без цены, например BALANCE
        publish("BUTTON_CLICK", {"action": query_data})

