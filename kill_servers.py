import sys
import psutil

def main():
    # Verificar que se haya pasado al menos el número de instancias
    if len(sys.argv) < 2:
        print("Uso: python kill_ports.py <número de instancias> [<puerto base>]")
        sys.exit(1)
    
    try:
        num_instances = int(sys.argv[1])
    except ValueError:
        print("El número de instancias debe ser un valor entero.")
        sys.exit(1)
    
    # Si se pasa el puerto base, se usa, de lo contrario, se usa 5000 por defecto
    base_port = 5000
    if len(sys.argv) > 2:
        try:
            base_port = int(sys.argv[2])
        except ValueError:
            print("El puerto base debe ser un valor entero. Se usará el puerto 5000 por defecto.")
            base_port = 5000

    # Definir el rango de puertos a evaluar
    target_ports = set(range(base_port, base_port + num_instances))
    print(f"Buscando procesos que escuchen en los puertos: {target_ports}")

    # Recorrer las conexiones de red y recolectar los pids que tienen puertos en el rango
    pids_to_kill = set()
    try:
        connections = psutil.net_connections(kind='inet')
    except Exception as e:
        print(f"Error obteniendo conexiones de red: {e}")
        sys.exit(1)

    for conn in connections:
        # Verificamos que la conexión esté en estado LISTEN
        if conn.status == psutil.CONN_LISTEN and conn.laddr:
            port = conn.laddr.port
            if port in target_ports:
                if conn.pid:
                    pids_to_kill.add(conn.pid)
    
    if not pids_to_kill:
        print("No se encontraron procesos escuchando en el rango de puertos especificado.")
        return

    # Intentar matar cada proceso identificado
    for pid in pids_to_kill:
        try:
            proc = psutil.Process(pid)
            print(f"Matando proceso {pid} ({proc.name()}) que escucha en uno de los puertos objetivo...")
            proc.kill()
        except Exception as e:
            print(f"No se pudo matar el proceso {pid}: {e}")

    print("Proceso finalizado. Se han terminado los procesos correspondientes.")

if __name__ == '__main__':
    main()
