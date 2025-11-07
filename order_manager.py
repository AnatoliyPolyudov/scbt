# order_manager.py
from event_bus import subscribe
from exchange import place_order
from telegram import send_balance

def handle_button_click(data):
    print("ORDER_MANAGER: Received button click:", data)
    
    action = data.get("action")
    
    # Для лимитных ордеров передается цена
    price = data.get("price")
    if price:
        price = float(price)

    if action == "BUY_LIMIT":
        print(f"Placing BUY LIMIT at {price}")
        place_order("BUY", price)
    elif action == "SELL_LIMIT":
        print(f"Placing SELL LIMIT at {price}")
        place_order("SELL", price)
    elif action == "BALANCE":
        print("Запрос баланса")
        send_balance()  # отправляем баланс в телеграм

# Подписка на событие кнопок
subscribe("BUTTON_CLICK", handle_button_click)
