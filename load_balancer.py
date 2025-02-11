import sys
import time
import requests
import threading
from flask import Flask, jsonify, request
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

SERVERS = []  # Lista de servidores activos
CHECK_INTERVAL = 2  # Intervalo de monitoreo en segundos
HISTORY_SIZE = 10  # Número de puntos históricos a usar para la regresión

# Almacenamiento para las cargas históricas
server_histories = {}


def check_server_status():
    """Monitorea continuamente el estado de los servidores y actualiza su carga."""
    global SERVERS
    while True:
        server_loads = []
        new_servers = []

        for server in SERVERS:
            try:
                response = requests.get(f"http://{server}/status", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    load = data.get("cpu", 100)  # Si no responde correctamente, asumimos 100% de carga
                    server_loads.append((server, load))
                    new_servers.append(server)  # Mantener servidores que responden
                    
                    # Actualizar la historia de cargas
                    if server not in server_histories:
                        server_histories[server] = []
                    server_histories[server].append(load)

                    # Limitar el tamaño de la historia para que no crezca indefinidamente
                    if len(server_histories[server]) > HISTORY_SIZE:
                        server_histories[server].pop(0)

            except requests.exceptions.RequestException:
                print(f"Servidor {server} no responde. Se eliminará temporalmente.")
        
        # Actualizar SERVERS solo con los que respondieron correctamente
        SERVERS[:] = new_servers

        # Ordenar servidores por menor carga
        server_loads.sort(key=lambda x: x[1])

        if server_loads:
            SERVERS[:] = [s[0] for s in server_loads]  # Actualizar la lista con los servidores ordenados
        
        print(f"Estado actual de los servidores: {SERVERS}")
        
        time.sleep(CHECK_INTERVAL)


def predict_load(server):
    """Predice la carga futura del servidor utilizando regresión lineal."""
    if server not in server_histories or len(server_histories[server]) < 2:
        return 100  # Si no hay suficientes datos históricos, asumimos una carga del 100%

    # Convertir las cargas históricas en un formato adecuado para la regresión lineal
    loads = server_histories[server]
    X = np.array(range(len(loads))).reshape(-1, 1)  # Índices de tiempo
    y = np.array(loads)  # Cargas

    # Crear el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)

    # Predecir la carga para el siguiente paso (tiempo)
    predicted_load = model.predict([[len(loads)]])
    return predicted_load[0]  # Retornar la carga predicha


@app.route('/balance', methods=['POST'])
def balance_request():
    """Redirige la petición al servidor con menor carga futura predicha."""
    if not SERVERS:
        return jsonify({'error': 'No hay servidores disponibles'}), 503
    
    if request.json is None:
        return jsonify({'error': 'Se requiere un JSON válido en la solicitud'}), 400

    # Predecir la carga futura para cada servidor
    server_predictions = [(server, predict_load(server)) for server in SERVERS]

    # Ordenar los servidores por su carga futura predicha (menor carga primero)
    server_predictions.sort(key=lambda x: x[1])

    best_server = server_predictions[0][0]  # El servidor con la carga más baja predicha
    try:
        response = requests.post(f"http://{best_server}/process", json=request.json, timeout=5)
        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({'error': f'Fallo al contactar el servidor {best_server}'}), 500


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            num_servers = int(sys.argv[1])
            if num_servers <= 0:
                raise ValueError("Debe haber al menos un servidor")
            SERVERS = [f"127.0.0.1:{5000 + i}" for i in range(num_servers)]
        except ValueError:
            print("Número de servidores inválido. Se usarán 5 por defecto.")
            SERVERS = [f"127.0.0.1:{5000 + i}" for i in range(5)]
    else:
        SERVERS = [f"127.0.0.1:{5000 + i}" for i in range(5)]

    print(f"Load Balancer activo en http://127.0.0.1:4000 gestionando {len(SERVERS)} servidores.")
    
    # Hilo para monitoreo continuo
    threading.Thread(target=check_server_status, daemon=True).start()

    app.run(host='0.0.0.0', port=4000)
