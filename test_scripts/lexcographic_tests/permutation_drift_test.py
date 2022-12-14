# A test to prove that the integer to Permutation function
# is lexicographical and generates in identical result compared
# to our original seed generation algorithm

from math import factorial

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

for x in range(100):
  for x in range(STEPS_BEGIN, STEPS_FINISH):
    ip_lex = next_lexicographic_permutation(ip_lex)
  
  int_to_perm = nthPerm(STEPS_FINISH,ip_int[:])
  
  if ip_lex == int_to_perm:
    print("{:,.0f} -> Perms Match".format(STEPS_FINISH))
    STEPS_BEGIN = STEPS_FINISH
    STEPS_FINISH += 10_000_000
  else:
    print("Deviation :")
    print(ip_lex)
    print(int_to_perm)

