from copy import deepcopy

def main():
  #1
  M = [[1, 2], [3, 4]]
  N = deepcopy(M)
  N[1].append(5)
  print(M)  # [[1, 2], [3, 4]]
  print(N)  # [[1, 2], [3, 4, 5]]

if __name__ == "__main__":
  main()
