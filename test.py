import matplotlib.pyplot as plt
import numpy as np

# Dati di esempio per il primo grafico
x1 = np.linspace(0, 10, 100)
y1 = np.sin(x1)

# Dati di esempio per il secondo grafico
x2 = np.linspace(0, 10, 100)
y2 = np.cos(x2)

# Creazione del primo grafico
plt.figure()
plt.plot(x1, y1)
plt.title('Primo Grafico: Funzione Seno')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()

# Quando si chiude il primo grafico, si apre il secondo
plt.figure()
plt.plot(x2, y2)
plt.title('Secondo Grafico: Funzione Coseno')
plt.xlabel('x')
plt.ylabel('cos(x)')
plt.grid(True)
plt.show()