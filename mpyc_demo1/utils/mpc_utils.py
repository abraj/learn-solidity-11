import secrets
import numpy as np
from mpyc.runtime import mpc
from utils.utils import create_matrix, hex_to_bytes

secint = mpc.SecInt(257)
secint16 = mpc.SecInt(16)
secfld = mpc.SecFld(2**8)

# NOTE: The returned secure int fits in 'at max' num_bits
# But, the actual #bits needed to hold the secure int might be 'less than' num_bits
def get_nbit_rand(secintType, num_bits):
  """Get a secure random int with 'maximum' #bits=num_bits"""
  rand = secintType(0)
  rand_bits = mpc.random_bits(mpc.SecInt(8), num_bits)
  for i, digit in enumerate(rand_bits[::-1]):
    rand += mpc.convert(digit, secintType) << i
  return rand

async def random_bytes(num_bytes):
  """Get an array of bytes (as int) of length num_bytes"""
  sec_rand_dec = get_nbit_rand(secint, 8 * num_bytes)
  rand_dec = await mpc.output(sec_rand_dec)
  padded_rand_hex = (hex(rand_dec)[2:]).zfill(num_bytes * 2)
  rand_bytes = hex_to_bytes(padded_rand_hex)
  return rand_bytes

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

def prepare_aes_key(dec_key):
  sec_bytes = convert_to_sec_bytes(dec_key)
  sec_bytes.pop(0)  # remove leading 0 (len 33 to len 32)
  if (len(sec_bytes) != 32):
    raise Exception(f'Invalid sec_bytes length: {len(sec_bytes)}')
  secret_block_32bytes = create_matrix(sec_bytes, 4, 8, dtype=object)
  return secret_block_32bytes

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

def mpc_pack(arr):
    np_arr = np.array(arr)
    shape = np_arr.shape
    np_arr = mpc.np_fromlist(np_arr.flatten().tolist())
    np_arr = mpc.np_reshape(np_arr, shape)
    return np_arr

@mpc.coroutine
async def to(x, secintType, secfldType):
  n = len(x)
  await mpc.returnType(secfldType, n)
  
  r = [secrets.randbits(1) for _ in range(n)]
  r_src = [secintType.field(1-2*a) for a in r]
  r_src = mpc.input([secintType(a) for a in r_src])
  r_src = list(map(list, zip(*r_src)))
  r_src = [mpc.prod(a) for a in r_src]
  r_src = [(1-a)/2 for a in r_src]
  c = mpc.vector_add(x, r_src)
  c = [mpc.lsb(a) for a in c]
  c = await mpc.output(c)

  r_tgt = [secfldType.field(a) for a in r]
  r_tgt = mpc.input([secfldType(a) for a in r_tgt])
  r_tgt = list(map(sum, zip(*r_tgt)))
  r_tgt = [a + b for a,b in zip(c, r_tgt)]
  return r_tgt

async def secint_to_secfld(a, secintType=secint16, secfldType=secfld):
  x = mpc.to_bits(a)
  x = to(x, secintType, secfldType)
  b = 0
  for xi in reversed(x[1:]):
    b += xi
    b *= secfldType.field(2)
  b += x[0]
  return b
