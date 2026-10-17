import numpy as np
from scipy.optimize import nnls
import pandas as pd
protein = float(input("Enter protein : "))
carb = float(input("Enter carb : "))
fats = float(input("Enter fats : "))
fiber = float(input("Enter fiber : "))
target_matrix = [protein,carb,fats,fiber]
ingredients = [0]

while True:
    Input = input("Enter your ingredient (type exit to exit) : ")
    if Input.lower() == "exit":
        if len(ingredients) <= 1:
            print("you have to choose atleast one ingredient!")
            continue
        else:
            break
    if int(Input) in ingredients:
        print("Already have those ingredient!")
        continue

    ingredients.append(int(Input))

def print_result(x,error,path,ingredient):
    df = pd.read_csv(path, sep=',',skiprows=lambda x: x not in ingredient)
    df = df.iloc[:, 1:8]
    
    total_protein = 0
    total_carb = 0
    total_fat = 0
    total_fiber = 0
    total_energy = 0
    total_price = 0
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
        total_price += round(weight*100,2)*df.iloc[i,6]
    print(f"Error : {np.round(error,3)}")
    print()
    print("Total :")
    print(f"Total_Protein : {round(total_protein,2)} g")
    print(f"Total Carb : {round(total_carb,2)} g")
    print(f"Total Fat : {round(total_fat,2)} g")
    print(f"Total_Fibre : {round(total_fiber,2)} g")
    print(f"Total_Energy : {round(total_energy,2)} kcal")
    print(f"Total_Price : {round(total_price,2)} Baht")

def load_ingredients(path,ingredient_list):
    #matrix = np.genfromtxt(path, delimiter=',', skip_header=1, usecols=(1, 2, 3, 4))
    df = pd.read_csv(path, sep=',',skiprows=lambda x: x not in ingredient_list)
    # .iloc[:, 1:] means "keep all rows (:), and keep columns from index 1 to the end"
    df = df.iloc[:, 2:6]
    print(df)
    matrix = df.to_numpy()
    matrix = np.transpose(matrix)
    return matrix

current_matrix = load_ingredients("smoothie_model_ready.csv",ingredients)
print(current_matrix)
x, residuals, rank, s = np.linalg.lstsq(current_matrix, target_matrix, rcond=None)

ls = 1
for i in x:
    if i < 0:
        ls = 0
        break 
if ls:
    print("USing LS")
    list_residuals = list(residuals)
    if len(list_residuals) <= 0:
        list_residuals.append(0)

    print_result(list(x),list_residuals[0],"smoothie_model_ready.csv",ingredients)
else:
    x_nnls, residual = nnls(current_matrix, target_matrix)
    print("USing NNLS")
    
    print_result(list(x_nnls),residual**2,"smoothie_model_ready.csv",ingredients)