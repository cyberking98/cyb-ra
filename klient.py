import socketio
import mss
import base64
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController

# SocketIO-klient för kommunikation med servern
sio = socketio.Client()
keyboard = KeyboardController()
mouse = MouseController()

@sio.event
def connect():
    print("Ansluten till servern.")

@sio.on("input")
def handle_input(data):
    if data['type'] == 'keyboard':
        keyboard.type(data['key'])
    elif data['type'] == 'mouse_move':
        mouse.position = (data['x'], data['y'])
    elif data['type'] == 'mouse_click':
        mouse.click(data['button'], data['count'])

@sio.event
def disconnect():
    print("Frånkopplad från servern.")

def stream_screen():
    """Fångar skärmbilder och skickar till servern."""
    with mss.mss() as sct:
        while True:
            screenshot = sct.grab(sct.monitors[1])  # Fånga skärmbilden
            # Minska bildstorleken för bättre prestanda
            img_bytes = base64.b64encode(screenshot.rgb).decode('utf-8')  
            if sio.connected:
                print(f"Skickar bilddata, storlek: {len(img_bytes)} bytes")
                sio.emit('screen', {'image': img_bytes}, namespace='/my_namespace')

if __name__ == '__main__':
    try:
        print("Försöker ansluta till servern...")
        sio.connect('http://localhost:5000', namespaces=['/my_namespace'])
        print(f"Ansluten till namespace: {sio.namespaces}")
        stream_screen()  # Starta skärmdelningen
    except Exception as e:
        print(f"Ett fel uppstod: {e}")
