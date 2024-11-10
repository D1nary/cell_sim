import numpy as np

data_2d = []

for k in range(10):
    for i in range(10):
        for j in range(10):
            new_row = [k, i, j]
            data_2d.append(new_row)

# Convert to numpy array if needed
data_2d = np.array(data_2d)

print(data_2d)