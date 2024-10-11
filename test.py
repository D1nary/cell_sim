import matplotlib.pyplot as plt
import numpy as np

# Generazione dei dati
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Primo grafico: Seno
plt.figure()
plt.plot(x, y1)
plt.title('Grafico del Seno')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()

# Secondo grafico: Coseno
plt.figure()
plt.plot(x, y2)
plt.title('Grafico del Coseno')
plt.xlabel('x')
plt.ylabel('cos(x)')
plt.grid(True)
plt.show()