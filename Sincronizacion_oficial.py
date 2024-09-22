import network
import socket
import machine

# Configuración de los servos
servo_hombro = machine.PWM(machine.Pin(0))
servo_codo = machine.PWM(machine.Pin(1))

servo_hombro.freq(50)
servo_codo.freq(50)

def map_angle_to_duty(angle, max_duty):
    return int((angle / 180) * max_duty)

def move_servo_hombro(angle):
    servo_hombro.duty_u16(map_angle_to_duty(180 - angle, 8192))  # Invertir el ángulo para el servo

def move_servo_codo(angle):
    servo_codo.duty_u16(map_angle_to_duty(180 - angle, 8192))  # Invertir el ángulo para el servo

# Conectar a Wi-Fi
ssid = 'FLIA RUBIANO_2G-Etb'
password = '3105807039'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Conectado a Wi-Fi')
print(wlan.ifconfig())

# Contenido HTML
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
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        renderer.setClearColor(0x000000);

        const base = new THREE.Mesh(new THREE.BoxGeometry(3, 0.5, 3), new THREE.MeshPhongMaterial({ color: 0x8B4513 }));
        base.position.y = -0.25;
        scene.add(base);

        const shoulder = new THREE.Group();
        const armMaterial = new THREE.MeshPhongMaterial({ color: 0xF5DEB3 });
        const elbowMaterial = new THREE.MeshPhongMaterial({ color: 0xADD8E6 });

        const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), armMaterial);
        arm.position.y = 2;
        shoulder.add(arm);

        const elbow = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 1, 32), elbowMaterial);
        elbow.position.set(0, 4, 0);
        shoulder.add(elbow);

        const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 4, 32), armMaterial);
        forearm.position.set(0, 2, 0);
        elbow.add(forearm);

        scene.add(shoulder);
        camera.position.set(0, 5, 10);
        camera.lookAt(0, 3, 0);

        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(0, 10, 10);
        scene.add(directionalLight);

        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();

        const controlContainer = document.createElement('div');
        controlContainer.className = 'controls';
        document.body.appendChild(controlContainer);

        const shoulderSlider = document.createElement('input');
        shoulderSlider.type = 'range';
        shoulderSlider.min = -90;
        shoulderSlider.max = 90;
        shoulderSlider.step = 1;
        shoulderSlider.value = 0;
        shoulderSlider.oninput = function() {
            const angle = parseFloat(this.value);
            shoulder.rotation.z = THREE.MathUtils.degToRad(-angle);
            fetch(/move_servo_hombro?angle=${angle + 90});
        };
        controlContainer.appendChild(document.createTextNode('Hombro (-90 a 90°): '));
        controlContainer.appendChild(shoulderSlider);

        const elbowSlider = document.createElement('input');
        elbowSlider.type = 'range';
        elbowSlider.min = 90;
        elbowSlider.max = 180;  // Rango de 90 a 180
        elbowSlider.step = 1;
        elbowSlider.value = 90;  // Inicial en 90 grados
        elbow.rotation.z = THREE.MathUtils.degToRad(90); // Cambiar la posición inicial del codo
        elbowSlider.oninput = function() {
            const angle = parseFloat(this.value);
            elbow.rotation.z = THREE.MathUtils.degToRad(angle);
            fetch(/move_servo_codo?angle=${angle}); // Mover el servo según el ángulo
        };
        controlContainer.appendChild(document.createElement('br'));
        controlContainer.appendChild(document.createTextNode('Codo (90-180°): '));
        controlContainer.appendChild(elbowSlider);
    </script>
</body>
</html>
"""

# Manejar solicitudes
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
        move_servo_hombro(angle)
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(b'Servo del hombro movido\n')
    elif 'GET /move_servo_codo' in request_str:
        angle = int(request_str.split('angle=')[1].split(' ')[0])
        move_servo_codo(angle)  # Usar el ángulo sin invertir
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
    print('Escuchando en', addr)

    while True:
        client, _ = server_socket.accept()
        handle_request(client)

start_server()