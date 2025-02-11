import sys
import subprocess

def main():
    # Verifica que se haya pasado un argumento
    if len(sys.argv) < 2:
        print("Uso: python script.py <número de instancias>")
        sys.exit(1)

    try:
        num_instances = int(sys.argv[1])
    except ValueError:
        print("El argumento debe ser un número entero.")
        sys.exit(1)
    
    base_port = 5000  # Puerto de inicio
    processes = []

    for i in range(num_instances):
        port = base_port + i
        print(f"Iniciando server.py en el puerto {port}...")
        # Lanza el proceso; usa sys.executable para asegurarte de que se utilice el intérprete actual de Python
        process = subprocess.Popen([sys.executable, "server.py", str(port)])
        processes.append(process)

    print(f"Se han iniciado {num_instances} instancias de server.py desde el puerto {base_port} hasta {base_port + num_instances - 1}.")
    
    # Opcional: Puedes esperar a que todos los procesos terminen (esto bloqueará el script)
    # for process in processes:
    #     process.wait()

if __name__ == '__main__':
    main()
