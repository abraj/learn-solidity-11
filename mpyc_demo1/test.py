import numpy as np
from copy import deepcopy

def main():
  # #1
  # M = [[1, 2], [3, 4]]
  # N = deepcopy(M)
  # N[1].append(5)
  # print(M)  # [[1, 2], [3, 4]]
  # print(N)  # [[1, 2], [3, 4, 5]]

  # #2
  # a = [1, 2, 3]
  # b = [4, 5, 6]
  # z = a + b
  # print(z)  # [1, 2, 3, 4, 5, 6]

  #3
  a = np.array([1, 2, 3])
  b = np.array([4, 5, 6])
  z = a + b
  print(z)  # [5 7 9]


if __name__ == "__main__":
  main()
