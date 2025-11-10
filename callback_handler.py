

# callback_handler.py
from event_bus import publish

# Глобальный флаг ручного управления
fvg_search_active = False

def handle_callback(query_data):
    global fvg_search_active
    
    print("CALLBACK_HANDLER: Received callback:", query_data)
    
    if query_data == "TOGGLE_FVG_SEARCH":
        # Переключаем состояние
        fvg_search_active = not fvg_search_active
        
        if fvg_search_active:
            print("🎯 FVG SEARCH ACTIVATED")
            publish("BUTTON_CLICK", {"action": "FVG_SEARCH_ON"})
        else:
            print("⏹️ FVG SEARCH DEACTIVATED")  
            publish("BUTTON_CLICK", {"action": "FVG_SEARCH_OFF"})
        
    else:
        # Остальные кнопки (BALANCE и другие)
        publish("BUTTON_CLICK", {"action": query_data})