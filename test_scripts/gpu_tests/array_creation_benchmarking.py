import numpy as np
import cupy as cp
import time

def next_lexicographic_permutation(x):
  
  i = len(x) - 2

  while i >= 0:
    if x[i] < x[i+1]:
      break
    else:
      i -= 1  
    if i < 0:
      return False
  
  j = len(x) - 1

  while j > i:
    if x[j] > x[i]:
      break
    else:
      j-= 1
  
  x[i], x[j] = x[j], x[i]
  reverse(x, i + 1)
  return x

def reverse(arr, i):
  if i > len(arr) - 1:
    return

  j = len(arr) - 1

  while i < j:
    arr[i], arr[j] = arr[j], arr[i]
    i += 1
    j -= 1

# New algorithm for calculating the Permutation based on a given integer
def int_to_perm(n,elems): # with n from 0
    output = []
    while len(elems) > 0:
        if(len(elems) == 1):
           output.append(elems[0])
           elems.remove(elems[0])
           continue
        sizeGroup = math.factorial(len(elems)-1)
        q,r = divmod(n,sizeGroup)
        v = elems[q]
        elems.remove(v)
        output.append(v)
        n = r
    return output
  
def perm_to_int(numbers): # takes the permutation list and converts it to an integer thanks ChatGPT :)
    base = len(numbers)
    lehmer = 0
    for i, num in enumerate(numbers):
        smaller = sum(1 for j in numbers[i + 1:] if j < num)
        lehmer += smaller * math.factorial(base - i - 1)
    return lehmer

# Create a numpy.random.Generator instance:
rng = np.random.default_rng()

# Define the length of each shuffled array
array_length = 33

# Define the number of arrays to generate
# cpu version does not need array and is typically doing 1_000_000_000 iterations
num_arrays = 5_000_000

arr = np.arange(array_length)
ip = np.arange(array_length)

print(f"{num_arrays:,} arrays")

example_one = np.full((num_arrays, 33), ip)
# example_two = np.zeros(num_arrays)

one_start_time = time.time()


for i in range(num_arrays):
  ip = next_lexicographic_permutation(ip)
  example_one[i] = ip

one_end_time = time.time()

print("Next Lex Perm Execution time: ", one_end_time - one_start_time, " seconds")
# print(example_one)  

# Create the input array
two_start_time = time.time()
example_two = np.arange(1000,num_arrays,1)

two_end_time = time.time()

print("Storing Integer for int_to_perm Execution time: ", two_end_time - two_start_time, " seconds")


# Create the original array
original_array = np.arange(33)

# Shuffle the original array
np.random.shuffle(original_array)

# Create the input array
input_array = np.zeros((num_arrays, 33), dtype=int)
three_start_time = time.time()
for i in range(num_arrays):
    input_array[i] = np.random.permutation(original_array)

three_end_time = time.time()

print("Random Permutation Execution time: ", three_end_time - three_start_time, " seconds")
