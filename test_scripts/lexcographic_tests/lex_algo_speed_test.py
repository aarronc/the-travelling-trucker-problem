# A test to prove that the integer to Permutation function
# is lexicographical and generates in identical result compared
# to our original seed generation algorithm

from math import factorial
import datetime

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

def nthPerm(n,elems):#with n from 0
    output = []
    while len(elems) > 0:
        if(len(elems) == 1):
           output.append(elems[0])
           elems.remove(elems[0])
           continue
        sizeGroup = factorial(len(elems)-1)
        q,r = divmod(n,sizeGroup)
        v = elems[q]
        elems.remove(v)
        output.append(v)
        n = r
    return output

STEPS_BEGIN = 0
STEPS_FINISH = 10_000_000

ip_lex = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
ip_int = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]

# 1 Million iteration test, old algorithm versus new algorithm

lex_start = datetime.datetime.now()
for x in range(1_000_000):
  ip_lex = next_lexicographic_permutation(ip_lex)
lex_finish = datetime.datetime.now()

print(f"Old Algorithm execution time => {lex_finish - lex_start}")

int_start = datetime.datetime.now()
for x in range(1_000_000):
  int_to_perm = nthPerm(x,ip_int[:])
int_finish = datetime.datetime.now()

print(f"New Algorithm execution time => {int_finish - int_start}")
