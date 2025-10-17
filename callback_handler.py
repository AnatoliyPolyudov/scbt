from event_bus import publish

def handle_callback(query_data):
    print("CALLBACK_HANDLER: Received callback:", query_data)
    
    # ИСПРАВЛЕНИЕ: обрабатываем рыночные ордера без цены
    if ':' in query_data:
        # Лимитные ордера: BUY_LIMIT:3800.50
        action, price = query_data.split(':')
        publish("BUTTON_CLICK", {"action": action, "price": price})
    else:
        # Рыночные ордера: BUY_MARKET, SELL_MARKET
        publish("BUTTON_CLICK", {"action": query_data, "price": None})