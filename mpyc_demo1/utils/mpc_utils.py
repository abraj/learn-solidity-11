from mpyc.runtime import mpc

def get_nbit_rand(secintType, num_bits):
  rand = secintType(0)
  rand_bits = mpc.random_bits(mpc.SecInt(8), num_bits)
  for i, digit in enumerate(rand_bits[::-1]):
    rand += mpc.convert(digit, secintType) << i
  return rand
