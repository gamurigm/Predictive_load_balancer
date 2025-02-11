import sys
import threading
import time
import random
import math
from flask import Flask, jsonify, request
import psutil

app = Flask(__name__)

# Variable global para almacenar la carga simulada
simulated_cpu_load = 0.0

def simulate_continuous_load():
    """Simula carga en la CPU procesando tareas cada cierto tiempo."""
    global simulated_cpu_load
    while True:
        # Variar la carga en el tiempo con una función sinusoidal
        t = time.time()
        simulated_cpu_load = max(0.1, abs(math.sin(t / 10)))  # Carga entre 0.1 y 1.0
        time.sleep(1)

@app.route('/status')
def status():
    """Devuelve la carga actual del servidor."""
    return jsonify({
        'cpu': psutil.cpu_percent(interval=0.1) + simulated_cpu_load,
        'ram': psutil.virtual_memory().percent
    })

@app.route('/process', methods=['POST'])
def process_request():
    """Simula procesamiento de una petición."""
    work_time = random.uniform(0.5, 2.5)  # Simula carga entre 0.5 y 2.5 segundos
    start_time = time.time()
    
    while time.time() - start_time < work_time:
        # Trabajo costoso (simulación)
        math.factorial(50000)
    
    return jsonify({'message': f'Procesado en {work_time:.2f} seg'})

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("El puerto debe ser un número entero.")

    # Iniciar simulación de carga en un hilo separado
    threading.Thread(target=simulate_continuous_load, daemon=True).start()

    print(f"Servidor iniciando en puerto {port}...")
    app.run(host='0.0.0.0', port=port)
