import network
import socket
import ure
import json
import time
import array
import uctypes
import machine  # Usar machine en lugar de board

# Configuración de los servos
servo_hombro = machine.PWM(machine.Pin(0))  # Hombro
servo_codo = machine.PWM(machine.Pin(1))    # Codo

servo_hombro.freq(50)
servo_codo.freq(50)

min_duty_hombro = 1638  # 0 grados para el servo del hombro
max_duty_hombro = 8192  # 180 grados para el servo del hombro

min_duty_codo = 1638     # 0 grados para el servo del codo
max_duty_codo = 8192     # 90 grados para el servo del codo

def map_angle_to_duty(angle, servo_type):
    if servo_type == 'hombro':
        return min_duty_hombro + (max_duty_hombro - min_duty_hombro) * angle // 180
    elif servo_type == 'codo':
        return min_duty_codo + (max_duty_codo - min_duty_codo) * angle // 90

# Funciones para controlar los servos
def move_servo_hombro(angle):
    servo_hombro.duty_u16(map_angle_to_duty(angle, 'hombro'))  # Cambiar a duty_u16()

def move_servo_codo(angle):
    servo_codo.duty_u16(map_angle_to_duty(angle, 'codo'))  # Cambiar a duty_u16()

# BACKEND MEM
memory = {}
struct_32 = {
    "value": uctypes.UINT32 | 0
}

def get_uctype(address):
    if address not in memory:
        memory[address] = uctypes.struct(address, struct_32)
    return memory[address]

def read_memory(address, rd):
    assert address % 4 == 0, f"The address {address} is not divisible by 4."
    return get_uctype(address).value

def write_memory(address, data):
    assert address % 4 == 0, f"The address {address} is not divisible by 4."
    get_uctype(address).value = data

def malloc(num_bytes, rd):
    assert num_bytes % 4 == 0, f"The number {num_bytes} is not divisible by 4."
    buff_0 = array.array('b', (10 + _ for _ in range(num_bytes)))
    dir0 = uctypes.addressof(buff_0)
    for address in range(dir0, dir0 + num_bytes, 4):
        write_memory(address, 0)
    return dir0

# Conectar a Wi-Fi
ssid = 'Oh_rigth'
password = 'culoacido'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Esperar conexión
while not wlan.isconnected():
    pass

print('Connected to Wi-Fi')
print(wlan.ifconfig())

# HTML content to serve
html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brazo Virtual</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; background-color: black; }  /* Fondo negro */
        canvas { display: block; }
        .controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(220, 220, 220, 0.9);
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <script>
        // Escena
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        renderer.setClearColor(0x000000); // Fondo negro

        // Crear base cuadrada
        const base = new THREE.Mesh(new THREE.BoxGeometry(3, 0.5, 3), new THREE.MeshPhongMaterial({ color: 0x8B4513 }));
        base.position.y = -0.25;
        scene.add(base);

        // Crear brazo robótico
        const shoulder = new THREE.Group();
        const armMaterial = new THREE.MeshPhongMaterial({ color: 0xF5DEB3 });
        const elbowMaterial = new THREE.MeshPhongMaterial({ color: 0xADD8E6 });

        // Brazo
        const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), armMaterial);
        arm.position.y = 2;
        shoulder.add(arm);

        // Codo
        const elbow = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 1, 32), elbowMaterial);
        elbow.position.set(0, 4, 0);
        shoulder.add(elbow);

        // Antebrazo
        const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), armMaterial);
        forearm.position.set(0, 2, 0);
        elbow.add(forearm);

        scene.add(shoulder);
        camera.position.set(0, 5, 10);
        camera.lookAt(0, 3, 0);

        // Luz
        const ambientLight = new THREE.AmbientLight(0x404040); // Luz suave
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(0, 10, 10);
        scene.add(directionalLight);

        // Función de animación
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();

        // Controles
        const controlContainer = document.createElement('div');
        controlContainer.className = 'controls';
        document.body.appendChild(controlContainer);

        // Control para el hombro
        const shoulderSlider = document.createElement('input');
        shoulderSlider.type = 'range';
        shoulderSlider.min = -45;
        shoulderSlider.max = 45;
        shoulderSlider.step = 1;
        shoulderSlider.value = 0;
        shoulderSlider.oninput = function() {
            const angle = parseFloat(this.value);
            shoulder.rotation.z = THREE.MathUtils.degToRad(angle);
            fetch(`/move_servo_hombro?angle=${angle + 45}`);
        };
        controlContainer.appendChild(document.createTextNode('Hombro (-45 a 45°): '));
        controlContainer.appendChild(shoulderSlider);

        // Control para el codo
        const elbowSlider = document.createElement('input');
        elbowSlider.type = 'range';
        elbowSlider.min = 0;
        elbowSlider.max = 90;
        elbowSlider.step = 1;
        elbowSlider.value = 0;
        elbowSlider.oninput = function() {
            const angle = parseFloat(this.value);
            elbow.rotation.z = THREE.MathUtils.degToRad(angle);
            fetch(`/move_servo_codo?angle=${angle}`);
        };
        controlContainer.appendChild(document.createElement('br'));
        controlContainer.appendChild(document.createTextNode('Codo (0-90°): '));
        controlContainer.appendChild(elbowSlider);
    </script>
</body>
</html>
"""

# Función para manejar solicitudes entrantes
def handle_request(client):
    request = client.recv(1024)
    request_str = request.decode('utf-8')
    
    if 'GET / ' in request_str:
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(html.encode('utf-8'))
        client.close()
    elif 'GET /move_servo_hombro' in request_str:
        angle = int(ure.search(r'angle=(\d+)', request_str).group(1))
        move_servo_hombro(angle)
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(b'Servo del hombro movido\n')
        client.close()
    elif 'GET /move_servo_codo' in request_str:
        angle = int(ure.search(r'angle=(\d+)', request_str).group(1))
        move_servo_codo(angle)
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(b'Servo del codo movido\n')
        client.close()

# Iniciar el servidor
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print('Listening on', addr)

    while True:
        client, _ = server_socket.accept()
        handle_request(client)

start_server()
