import numpy as np
from scipy.optimize import nnls
import pandas as pd
protein = float(input("Enter protein : "))
carb = float(input("Enter carb : "))
fats = float(input("Enter fats : "))
fiber = float(input("Enter fiber : "))
ingredient = [0,1,2]
target_matrix = [protein,carb,fats,fiber]

def print_result(x,error,path,ingredient):
    df = pd.read_csv(path, sep='\t',skiprows=lambda x: x not in [0,9,98,7,48,50])
    df = df.iloc[:, 1:7]
    
    total_protein = 0
    total_carb = 0
    total_fat = 0
    total_fiber = 0
    total_energy = 0
    print("Ingredient_List : ")
    for i in range(len(x)):
        name = df.iloc[i, 0]
        weight = round(x[i],7)
        print(f"{name} : {round(weight*100,2)} g")
        total_protein += weight*df.iloc[i,1]
        total_carb += weight*df.iloc[i,2]
        total_fat += weight*df.iloc[i,3]
        total_fiber += weight*df.iloc[i,4]
        total_energy += weight*df.iloc[i,5]
    print(f"Error : {np.round(error,3)}")
    print("Total :")
    print(f"Total_Protein : {round(total_protein,2)} g")
    print(f"Total Carb : {round(total_carb,2)} g")
    print(f"Total Fat : {round(total_fat,2)} g")
    print(f"Total_Fibre : {round(total_fiber,2)} g")
    print(f"Total_Energy : {round(total_energy,2)} kcal")

def load_ingredients(path,ingredient_list):
    #matrix = np.genfromtxt(path, delimiter=',', skip_header=1, usecols=(1, 2, 3, 4))
    df = pd.read_csv(path, sep='\t',skiprows=lambda x: x not in [0,9,98,7,48,50])
    # .iloc[:, 1:] means "keep all rows (:), and keep columns from index 1 to the end"
    df = df.iloc[:, 2:6]
    print(df)
    matrix = df.to_numpy()
    matrix = np.transpose(matrix)
    return matrix
    
x, residuals, rank, s = np.linalg.lstsq(load_ingredients("FoodData_Central_foundation_food_json_2026-04-30/smoothie_model_ready.csv",ingredient), target_matrix, rcond=None)
x_nnls, residual = nnls(load_ingredients("FoodData_Central_foundation_food_json_2026-04-30/smoothie_model_ready.csv",ingredient), target_matrix)
ls = 1
for i in x:
    if i < 0:
        ls = 0
        break
if ls:
    print("USing LS")
    
    print_result(list(x),residuals,"FoodData_Central_foundation_food_json_2026-04-30/smoothie_model_ready.csv",ingredient)
else:
    print("USing NNLS")
    
    print_result(list(x_nnls),residual,"FoodData_Central_foundation_food_json_2026-04-30/smoothie_model_ready.csv",ingredient)