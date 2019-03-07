import math

#Returns a new list that has a euclidean norm as given
def euclidean_norm(input_list, desired_norm = 1.0):
    new_list = []
    norm = sum([x**2 for x in input_list])
    if norm == 0.0:
        return input_list
    new_list = [math.sqrt((x**2)/norm) for x in input_list]
    return new_list

def dot_product(list_one, list_two):
    return sum([a*b for a,b in zip(list_one,list_two)])
