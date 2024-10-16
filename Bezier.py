import network
import socket
import machine
import time

# Definir servos
servo_hombro = machine.PWM(machine.Pin(0))
servo_codo = machine.PWM(machine.Pin(1))

servo_hombro.freq(50)
servo_codo.freq(50)

def map_angle_to_duty(angle, max_duty):
    return int((angle / 180) * max_duty)

def move_servo_hombro(angle):
    servo_hombro.duty_u16(map_angle_to_duty(180 - angle, 8192))

def move_servo_codo(angle):
    servo_codo.duty_u16(map_angle_to_duty(180 - angle, 8192))

# Función para mover el servo suavemente usando una curva de Bézier
def bezier_interpolation(t, p0, p1, p2):
    """Interpolación cúbica de Bézier."""
    return (1-t)**2 * p0 + 2 * (1-t) * t * p1 + t**2 * p2

def smooth_move_servo(servo_move_function, start_angle, end_angle, duration=1.0):
    steps = 50  # Dividir en 50 pasos para el movimiento suave
    if start_angle < end_angle:
        p0, p1, p2 = start_angle, (start_angle + end_angle) / 2, end_angle
    else:
        p0, p1, p2 = start_angle, (start_angle + end_angle) / 2, end_angle
    
    for step in range(steps + 1):
        t = step / steps
        angle = bezier_interpolation(t, p0, p1, p2)
        servo_move_function(angle)
        time.sleep(duration / steps)


# Conexión Wi-Fi
ssid = 'FLIA RUBIANO_2G-Etb'
password = '3105807039'


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Conectado a Wi-Fi')
print(wlan.ifconfig())

# HTML para controlar los servos
html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brazo Virtual</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; background-color: black; }
        canvas { display: block; }
        .controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(220, 220, 220, 0.9);
            padding: 10px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // Definir diferentes materiales para las partes del brazo
        const materialBase = new THREE.MeshBasicMaterial({ color: 0x8B4513 });  // Base color marrón
        const materialArm = new THREE.MeshBasicMaterial({ color: 0xFFD700 });  // Brazo superior color dorado
        const materialElbow = new THREE.MeshBasicMaterial({ color: 0xFF4500 });  // Codo color naranja fuerte
        const materialForearm = new THREE.MeshBasicMaterial({ color: 0x1E90FF });  // Antebrazo color azul

        // Crear la base
        const base = new THREE.Mesh(new THREE.BoxGeometry(3, 0.5, 3), materialBase);
        base.position.y = -0.25;
        scene.add(base);

        // Crear el hombro y brazo superior
        const shoulder = new THREE.Group();
        const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), materialArm);
        arm.position.y = 2;
        shoulder.add(arm);

        // Crear el codo
        const elbow = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 1, 32), materialElbow);
        elbow.position.set(0, 4, 0);
        shoulder.add(elbow);

        // Crear el antebrazo
        const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), materialForearm);
        forearm.position.set(0, 2, 0);
        elbow.add(forearm);

        // Añadir el conjunto del hombro a la escena
        scene.add(shoulder);
        camera.position.set(0, 5, 10);
        camera.lookAt(0, 3, 0);

        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();

        // Controles de los sliders
        const controlContainer = document.createElement('div');
        controlContainer.className = 'controls';
        document.body.appendChild(controlContainer);

        // Slider del hombro
        const shoulderSlider = document.createElement('input');
        shoulderSlider.type = 'range';
        shoulderSlider.min = -90;
        shoulderSlider.max = 90;
        shoulderSlider.value = 0;
        shoulderSlider.oninput = function() {
            const angle = parseFloat(this.value);
            shoulder.rotation.z = THREE.MathUtils.degToRad(-angle);
            fetch(`/move_servo_hombro?angle=${angle + 90}`);
        };
        controlContainer.appendChild(document.createTextNode('Hombro: '));
        controlContainer.appendChild(shoulderSlider);

        // Slider del codo
        const elbowSlider = document.createElement('input');
        elbowSlider.type = 'range';
        elbowSlider.min = 90;
        elbowSlider.max = 150;
        elbowSlider.value = 90;
        elbow.rotation.z = THREE.MathUtils.degToRad(90);
        elbowSlider.oninput = function() {
            const angle = parseFloat(this.value);
            elbow.rotation.z = THREE.MathUtils.degToRad(angle);
            fetch(`/move_servo_codo?angle=${angle}`);
        };
        controlContainer.appendChild(document.createElement('br'));
        controlContainer.appendChild(document.createTextNode('Codo: '));
        controlContainer.appendChild(elbowSlider);
    </script>
</body>
</html>
"""

# Manejar solicitudes del servidor
def handle_request(client):
    request = client.recv(1024)
    request_str = request.decode('utf-8')

    if 'GET / ' in request_str:
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(html.encode('utf-8'))
    elif 'GET /move_servo_hombro' in request_str:
        angle = int(request_str.split('angle=')[1].split(' ')[0])
        smooth_move_servo(move_servo_hombro, 90, angle)  # Mover suavemente el hombro
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(b'Servo del hombro movido\n')
    elif 'GET /move_servo_codo' in request_str:
        angle = int(request_str.split('angle=')[1].split(' ')[0])
        smooth_move_servo(move_servo_codo, 90, angle)  # Mover suavemente el codo
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(b'Servo del codo movido\n')
    
    client.close()

# Iniciar servidor
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print('Escuchando en', addr)

    while True:
        client, _ = server_socket.accept()
        handle_request(client)

start_server()
