import math
import numpy as np

def conv(rad, x):
    denom = 3.8  # //sqrt(2) * 2.7
    return math.erf((rad - x) / denom) - math.erf((-rad - x) / denom)

def get_multiplicator(dose, radius):
    return dose / conv(14, 0)

def scale(radius, x, multiplicator):
    print(x,x * 10 / radius)
    return multiplicator * conv(14, x * 10 / radius)

def main():
    radius = 14
    dose  = 10
    multiplicator = get_multiplicator(dose, radius)
    for x in range(-30, 31):
        value = scale(radius, x, multiplicator) # x = distanza dal centro
        # print(f"x = {x}, scale = {value}")

if __name__ == "__main__":
    main()
