import numpy as np
from scipy.optimize import nnls
import pandas as pd
protein = float(input("Enter protein : "))
carb = float(input("Enter carb : "))
fats = float(input("Enter fats : "))
fiber = float(input("Enter fiber : "))

target_matrix = [[protein],[carb],[fats],[fiber]]

def load_ingredients(path):
    #matrix = np.genfromtxt(path, delimiter=',', skip_header=1, usecols=(1, 2, 3, 4))
    df = pd.read_csv(path, skiprows=lambda x: x not in [0,1,2,3])
    dm = pd.read_csv(path, skiprows=lambda x: x not in [0,1,2,3,4])
    # .iloc[:, 1:] means "keep all rows (:), and keep columns from index 1 to the end"
    df = df.iloc[:, 1:]
    dm = dm.iloc[:, 1:]
    matrix = df.to_numpy()
    print(np.transpose(matrix))

    # return matrix
    return np.transpose(matrix)
x, residuals, rank, s = np.linalg.lstsq(load_ingredients("Module/ingredients.csv"), target_matrix, rcond=None)
x_nnls, residual = nnls(load_ingredients("Module/ingredients.csv"), target_matrix)
ls = 1
for i in x:
    if i < 0:
        ls = 0
        break
if ls:
    print("USing LS",end='')
    print(x,np.round(residuals,3))
else:
    print("USing NNLS",end='')
    print(x_nnls,np.round(residual,3))