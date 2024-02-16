

def find_slow(arr, k): 
    for el in arr: 
        if el == k: 
            return True 
    return False 


def find_and_sort(arr, k): 
    arr.sort() 
    for el in arr: 
        if el == k:
            return True 
    return False 


def some_print(): 
    print("some text")



for _ in range(10_000): 
    find_slow([1, 2, 3, 6, 2, 4], 10)
    find_and_sort([1, 1, 1, 1, 2, 2, 8] + list(range(100, 1, -1)), -2) 


some_print()

