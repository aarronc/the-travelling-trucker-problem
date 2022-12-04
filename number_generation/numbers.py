import math
import datetime
import sqlite3
import uuid

DB = sqlite3.connect("33_fact_iterations.db")
d = DB.cursor()

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

d.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='numbers' ''')

if d.fetchone()[0]==1: 
  print('Number table exists.')
  row = DB.execute("SELECT * FROM numbers ORDER by iteration DESC LIMIT 1").fetchall()
  row = row[0]
  iteration = row[0]
  perm = eval(row[1])
  print(f"Resuming from {iteration +1:,}")
  identifier = row[2]
else:
  print('Table does not exist... creating now')
  DB.execute(''' CREATE TABLE numbers
             (iteration integer,
             sequence varchar(128),
             identifier varchar(37),
             send_count integer,
             result_1 text,
             result_2 text,
             result_3 text,
             sent_at varchar(30),
             finished_at varchar(30)
             born_on varchar(30),
             )''')
  DB.commit()
  iteration = 0
  perm = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
  identifier = uuid.uuid4()

total_permutations = int(math.factorial(33))
y = 0
for x in range(iteration,total_permutations):
  perm = next_lexicographic_permutation(perm)
  if y == 10_000_000:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] {x:,} {perm}")
    DB.execute("INSERT INTO numbers VALUES (?,?,?,?,?,?,?,?,?,?)",(x, str(perm), str(uuid.uuid4()), 0, None, None, None, None, None, str(timestamp)))
    DB.commit()
    y = 0
  y+= 1