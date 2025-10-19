from event_bus import publish

def handle_callback(query_data):
    print("CALLBACK_HANDLER: Received callback:", query_data)
    
    # Обрабатываем только лимитные ордера
if ':' in query_data:
    action, price = query_data.split(':')
    publish("BUTTON_CLICK", {"action": action, "price": price})