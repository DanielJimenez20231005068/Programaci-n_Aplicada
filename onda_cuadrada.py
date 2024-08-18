def generador_senales(x, f, a):
    T = 1 / f 
#convertimos la frecuencia a periodo para usar los puntos de la grafica 0s y 1s
    t = x/512
#definimos una ecuacion que relaciona linealmente los pixeles hor con el periodo

#Dicha ecuacion fue hecha con los puntos (0,0) y (512,1)    
    
    y = -6.49 * a + 64
#De igual forma sacamos una ecuacion que relaciona linealmente los pixeles ver con la amplitud
#puntos (10,0) y (-10, 128)    
    
    posicion = t % T
#usamos un modulo para clasificar el punto en x y asignarle un punto en Y + o -    

    if posicion < t:        
        y = y/2
    else:
        y = - y/2

    return int (y), T 

#asignamos valores
a = 90
f = 15
x = 29

# Llamada a la función
y, T = generador_senales(x, f, a)


print("El periodo es:")
print(T)
print("La coordenada en Y que le corresponde a la coordenada en X solicitada es:")
print(y)