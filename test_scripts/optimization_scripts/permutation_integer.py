# converts an integer into a permutation with just the sorted starting array

from math import factorial


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
  
ip = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]

# found this at https://stackoverflow.com/a/25436298
# editied it to make it output a nice list
int_to_perm = nthPerm(1117122470000000,ip[:])
print(int_to_perm)

# Expected Output [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,22,24,28,30,21,31,27,32,23,17,20,26,25,29,19,18]
# Actual Output   [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,22,24,28,30,21,31,27,32,23,17,20,26,19,25,18,29]
          