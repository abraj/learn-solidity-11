import secrets
import numpy as np
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

def matrix_xor(A, B):
  secfld = mpc.SecFld(2**8)
  a_shape = np.array(A).shape
  b_shape = np.array(B).shape
  if a_shape != b_shape:
    raise Exception(f'Mismatched shape while performing xor: {a_shape}, {b_shape}')

  n, m = a_shape
  result = np.zeros((n, m), dtype=secfld)
  for i in range(n):
    for j in range(m):
      result[i][j] = A[i][j] ^ B[i][j]

  result = mpc.np_fromlist(sum(result.tolist(), []))
  result = mpc.np_reshape(result, a_shape)
  return result

@mpc.coroutine
async def to(x):
  secint = mpc.SecInt()
  secfld256 = mpc.SecFld(2**8)
  n = len(x)
  await mpc.returnType(secfld256, n)
  
  r = [secrets.randbits(1) for _ in range(n)]
  r_src = [secint.field(1-2*a) for a in r]
  r_src = mpc.input([secint(a) for a in r_src])
  r_src = list(map(list, zip(*r_src)))
  r_src = [mpc.prod(a) for a in r_src]
  r_src = [(1-a)/2 for a in r_src]
  c = mpc.vector_add(x, r_src)
  c = [mpc.lsb(a) for a in c]
  c = await mpc.output(c)

  r_tgt = [secfld256.field(a) for a in r]
  r_tgt = mpc.input([secfld256(a) for a in r_tgt])
  r_tgt = list(map(sum, zip(*r_tgt)))
  r_tgt = [a + b for a,b in zip(c, r_tgt)]
  return r_tgt

async def secintToSecfld(a):
  secfld256 = mpc.SecFld(2**8)
  x = mpc.to_bits(a)
  x = to(x)
  b = 0
  for xi in reversed(x[1:]):
    b += xi
    b *= secfld256.field(2)
  b += x[0]
  return b
