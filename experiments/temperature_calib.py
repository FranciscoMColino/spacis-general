import numpy as np
from sympy import Eq, solve, symbols

x, y = symbols('x y')

recorded_list = [
    [20, 176, 41.2],
    [23, 56, 44],
    [23, 72, 44.7],
    [23, 184, 45.1],
    [20, 70, 44.2],
    [18, 224, 40.1],
    [17, 24, 37.6],
    [16, 16, 35.9],
    [15, 136, 34.5],
    [15, 0, 33.6],
    [14, 188, 32],
    [13, 240, 28.4],
    [13, 184, 27.4]
]

results = []

for i in range(len(recorded_list)):
    for j in range(i+1, len(recorded_list)):
        eq1 = Eq(recorded_list[i][0] * x + recorded_list[i][1] * y, recorded_list[i][2])
        eq2 = Eq(recorded_list[j][0] * x + recorded_list[j][1] * y, recorded_list[j][2])
        result = solve((eq1, eq2), (x, y))
        # 
        results.append([value for value in result.values()])

print(results)

# average the results using numpy
results = np.array(results)
results_avg = np.average(results, axis=0)

print(results_avg)
