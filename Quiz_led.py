import socketpool
import wifi
import board
import digitalio

# Configuracion del pin del LED
led = digitalio.DigitalInOut(board.GP13)
led.direction = digitalio.Direction.OUTPUT

wifi.radio.connect("Ejemplo", "12345678")
pool = socketpool.SocketPool(wifi.radio)

print("wifi.radio", wifi.radio.hostname, wifi.radio.ipv4_address)
s = pool.socket()
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    buffer = bytearray(1024)  # Create a mutable buffer
    bytes_received, address = conn.recvfrom_into(buffer)  # Receive data into the buffer and get the sender's address
    print("Received from:", address)
    print("Received data:", buffer[:bytes_received])  # Print received data
    
    request = buffer[:bytes_received].decode('utf-8')  # Convert received data to string
    print("Solicitud recibida:", request)  # Print received request

    if "GET /arriba" in request:  # Cambia "arriba" por "encendido"
        print("Led encendido")
        led.value = True 

    elif "GET /abajo" in request:  # Cambia "abajo" por "apagado"
        print("Led apagado")
        led.value = False 

    response = """
<!DOCTYPE html>
<html>
<head>
    <title>Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; } 
        h1 { color: #333; }
        .button-container {
            display: flex;
            justify-content: space-around;
            margin-top: 50px;
        }
        .button {
            padding: 15px 30px;
            font-size: 18px;
            color: white;
            background-color: #007BFF;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
        }
        .button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Control Panel</h1>
    <div class="button-container">
        <a href="/arriba"><div class="button">Encendido</div></a>
        <a href="/abajo"><div class="button">Apagado</div></a>
    </div>
</body>
</html>
"""

    conn.send(response)
    conn.close()
