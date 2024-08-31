import math

def taylor_ln(x, terminos=10):
    if x <= 0:
        raise ValueError("x debe ser mayor que 0")
    
    # Elegir y para mejorar la convergencia
    y = 1
    if x > 2:
        y = math.floor(x)
        x = x / y
    
    resultado = 0
    for n in range(1, terminos + 1):
        term = ((-1)**(n+1)) * ((x-1)**n) / n
        resultado += term
    
    # Sumar el ln(y)
    resultado += math.log(y) #Se suma ln(y) al resultado final. Previamente dividimos x por y, y necesitamos ajustar el resultado
    
    return resultado

# Uso
x = 9
terminos = 10   
approx = taylor_ln(x, terminos)
print(f"ln({x}) ≈ {approx} con {terminos} términos de la serie de Taylor")
