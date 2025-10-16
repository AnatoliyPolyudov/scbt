subscribers = {}

def subscribe(event_type, callback):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(callback)

def publish(event_type, data):
    if event_type in subscribers:
        for callback in subscribers[event_type]:
            callback(data)
