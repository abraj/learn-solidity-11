from mpyc.runtime import mpc

secint16 = mpc.SecInt(16)

def get_nbit_rand(secintType, num_bits):
  rand = secintType(0)
  rand_bits = mpc.random_bits(mpc.SecInt(8), num_bits)
  for i, digit in enumerate(rand_bits[::-1]):
    rand += mpc.convert(digit, secintType) << i
  return rand

def get_ascii_code(c):
  code = mpc.if_else(mpc.eq(c, 10), 97, 
      mpc.if_else(mpc.eq(c, 11), 98, 
      mpc.if_else(mpc.eq(c, 12), 99, 
      mpc.if_else(mpc.eq(c, 13), 100, 
      mpc.if_else(mpc.eq(c, 14), 101, 
      mpc.if_else(mpc.eq(c, 15), 102, 
      mpc.if_else(mpc.eq(c, 0), 48, 
      mpc.if_else(mpc.eq(c, 1), 49, 
      mpc.if_else(mpc.eq(c, 2), 50, 
      mpc.if_else(mpc.eq(c, 3), 51, 
      mpc.if_else(mpc.eq(c, 4), 52, 
      mpc.if_else(mpc.eq(c, 5), 53, 
      mpc.if_else(mpc.eq(c, 6), 54, 
      mpc.if_else(mpc.eq(c, 7), 55, 
      mpc.if_else(mpc.eq(c, 8), 56, 
      mpc.if_else(mpc.eq(c, 9), 57, 0))))))))))))))))
  return code

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

def convert_to_hex_ascii(sec_dec, secintType=secint16):
  sec_bytes = convert_to_sec_bytes(sec_dec, secintType)

  # Convert each byte to hexadecimal and then to ASCII values
  hex_ascii_array = []
  for byte in sec_bytes:
    a = byte // 16
    b = byte % 16
    a = get_ascii_code(a)
    b = get_ascii_code(b)
    hex_ascii_array.extend([a, b])

  return hex_ascii_array
