from mpyc.runtime import mpc

secint16 = mpc.SecInt(16)

def get_nbit_rand(secintType, num_bits):
  rand = secintType(0)
  rand_bits = mpc.random_bits(mpc.SecInt(8), num_bits)
  for i, digit in enumerate(rand_bits[::-1]):
    rand += mpc.convert(digit, secintType) << i
  return rand

def convert_to_sec_bytes(sec_dec, secintType=secint16):
  # Get the number of bytes needed for the shared integer
  num_bytes = (sec_dec.bit_length + 7) // 8

  # NOTE: the following does not work for smaller `secintType`s like SecInt16, etc.
  # hex_bytes = [mpc.and_(mpc.convert(sec_dec >> (8 * i), secintType), secintType(0xFF)) for i in range(num_bytes)]

  # Convert shared integer to bytes array
  base = sec_dec
  sec_bytes = []
  for _ in range(num_bytes):
    item = mpc.convert(base % 2**8, secintType)
    base = base // 2**8
    sec_bytes.append(item)

  sec_bytes = sec_bytes[::-1]

  return sec_bytes
