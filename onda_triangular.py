def generador_senales(x, f, a, tipo='sinusoidal'):
    T = 1 / f 
    t = x / 512
    
    if tipo == 'sinusoidal':
        y = -6.49 * a + 64
        posicion = t % T
        if posicion < t:        
            y = y / 2
        else:
            y = - y / 2
    elif tipo == 'diente_de_sierra':
        y = 2 * a * (t / T - int(t / T + 0.5))

    return int(y), T

def menu():
    while True:
        print("\nSeleccione el tipo de señal a generar:")
        print("1. Onda Sinusoidal")
        print("2. Onda Diente de Sierra")
        print("3. Salir")
        opcion = input("Ingrese el número de la opción deseada: ")

        if opcion == '1':
            tipo = 'sinusoidal'
        elif opcion == '2':
            tipo = 'diente_de_sierra'
        elif opcion == '3':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida.")
            continue

        a = int(input("Ingrese la amplitud: "))
        f = int(input("Ingrese la frecuencia: "))
        x = int(input("Ingrese la coordenada X: "))

        y, T = generador_senales(x, f, a, tipo)
        print("El periodo es:", T)
        print("La coordenada en Y que le corresponde a la coordenada en X solicitada es:", y)

menu()
