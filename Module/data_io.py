#import numpy as np
import pandas as pd

def load_ingredients(path):
    #matrix = np.genfromtxt(path, delimiter=',', skip_header=1, usecols=(1, 2, 3, 4))
    df = pd.read_csv(path, skiprows=lambda x: x not in [0,1])
    dm = pd.read_csv(path, skiprows=lambda x: x not in [0,1,2,3,4])
    # .iloc[:, 1:] means "keep all rows (:), and keep columns from index 1 to the end"
    df = df.iloc[:, 1:]
    dm = dm.iloc[:, 1:]
    matrix = df.to_numpy()
    matrix2 = dm.to_numpy()
    combine = matrix @ matrix2

    
    print(combine)


def build_matrix(ingredients):
    pass

def build_target(targets):
    pass

load_ingredients("Module/ingredients.csv")