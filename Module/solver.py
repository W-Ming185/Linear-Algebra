import numpy as np
from scipy.optimize import lsq_linear
import pandas as pd
protein = float(input("Enter protein : "))
carb = float(input("Enter carb : "))
fats = float(input("Enter fats : "))
fiber = float(input("Enter fiber : "))
target_matrix = [protein,carb,fats,fiber]
ingredients = [0]
min_bounds = []

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
    while True:
        min_g = input(f"Enter minimum amount for ingredient {Input} (g) : ")
        if min_g is not None and min_g.isdigit():
            break
        print("Try again.")
    min_bounds.append(float(min_g)/100.00)
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
    # print(df)
    matrix = df.to_numpy()
    matrix = np.transpose(matrix)
    return matrix

lb = np.array(min_bounds)
current_matrix = load_ingredients("smoothie_model_ready.csv",ingredients)
result = lsq_linear(current_matrix, target_matrix, bounds=(lb, np.inf))

error = np.sum(result.fun ** 2)
print("USing LS")

print_result(list(result.x), error, "smoothie_model_ready.csv", ingredients)
