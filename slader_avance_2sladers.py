import socketpool
import wifi
import pwmio
import board

#conectar al celular 
wifi.radio.connect("Maricon", "Juan2004")
pool = socketpool.SocketPool(wifi.radio)

print("wifi.radio:", wifi.radio.hostname, wifi.radio.ipv4_address)
s = pool.socket()
s.bind(('', 80))
s.listen(5)

# Configuración de los servomotores
servo1 = pwmio.PWMOut(board.GP0, frequency=50)  
servo2 = pwmio.PWMOut(board.GP1, frequency=50)  

min_duty = 1638  
max_duty = 8192  

# Función para mapear el ángulo a un valor de duty cycle
def map_angle_to_duty(angle, min_angle=0, max_angle=180):
    return min_duty + (max_duty - min_duty) * (angle - min_angle) // (max_angle - min_angle)

# inicio servo motores
servo1.duty_cycle = map_angle_to_duty(0)  # Servo 1: 0 grados
servo2.duty_cycle = map_angle_to_duty(0, max_angle=90)  #servo numero 2 esta limitado a 90
print("Servos inicializados")

# Página HTML 
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Control de Sliders</title>
</head>
<body>
    <h1>Control de Servos</h1>
    <label for="slider1">Ángulo del Servo 1:</label>
    <input type="range" id="slider1" min="0" max="180" value="90" oninput="updateValue1(this.value)">
    <p>Ángulo seleccionado para Servo 1: <span id="angleValue1">90</span> grados</p>

    <label for="slider2">Ángulo del Servo 2:</label>
    <input type="range" id="slider2" min="0" max="90" value="45" oninput="updateValue2(this.value)">
    <p>Ángulo seleccionado para Servo 2: <span id="angleValue2">45</span> grados</p>

    <script>
        function updateValue1(value) {
            document.getElementById("angleValue1").innerText = value;
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/set_angle1?value=" + value, true);
            xhr.send();
        }

        function updateValue2(value) {
            document.getElementById("angleValue2").innerText = value;
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/set_angle2?value=" + value, true);
            xhr.send();
        }
    </script>
</body>
</html>
"""

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    
    # Recibir datos del cliente
    buffer = bytearray(1024)
    bytes_received, address = conn.recvfrom_into(buffer)
    request = buffer[:bytes_received].decode('utf-8')
    print("Received request:", request)

    # Analizar la solicitud del cliente
    if "GET / " in request:
        # Si la solicitud es para la página principal
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html
        conn.send(response.encode('utf-8'))
    elif "GET /set_angle1?value=" in request:
        # Si la solicitud es para ajustar el ángulo del primer servo
        angle1 = int(request.split("value=")[-1].split(" ")[0])
        print(f"Ángulo recibido para Servo 1: {angle1} grados")
        
        # Ajustar el primer servomotor basado en el ángulo recibido
        duty_cycle1 = map_angle_to_duty(angle1)
        servo1.duty_cycle = duty_cycle1
        print(f"Duty cycle ajustado para Servo 1: {duty_cycle1}")
        
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nÁngulo recibido para Servo 1"
        conn.send(response.encode('utf-8'))
    elif "GET /set_angle2?value=" in request:
        # Si la solicitud es para ajustar el ángulo del segundo servo
        angle2 = int(request.split("value=")[-1].split(" ")[0])
        print(f"Ángulo recibido para Servo 2: {angle2} grados")
        
        # Ajustar el segundo servomotor basado en el ángulo recibido
        duty_cycle2 = map_angle_to_duty(angle2, max_angle=90)
        servo2.duty_cycle = duty_cycle2
        print(f"Duty cycle ajustado para Servo 2: {duty_cycle2}")
        
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nÁngulo recibido para Servo 2"
        conn.send(response.encode('utf-8'))

    conn.close()


