import sys
import numpy as np
from mpyc.runtime import mpc
from mpyc.seclists import seclist
from secret_sharing.shamir import shamir_split, shamir_reconstruct
from utils.mpc_utils import get_nbit_rand
from hashing.sha3_plus import sha3_256_hash_bits

KEY_SIZE = 32  # 32 bytes (256 bits)
secint = mpc.SecInt(257)
secint16 = mpc.SecInt(16)
secfld1 = mpc.SecFld(2)

threshold = 2            # Minimum number of shares required for reconstruction
n_parties = 3            # Total number of parties

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

async def get_hex_commitment(dec_val):
  secintType = secint16

  # Get the number of bytes needed for the shared integer
  num_bytes = (dec_val.bit_length + 7) // 8

  # NOTE: the following does not work for smaller `secintType`s like SecInt16, etc.
  # hex_bytes = [mpc.and_(mpc.convert(dec_val >> (8 * i), secintType), secintType(0xFF)) for i in range(num_bytes)]

  # Convert shared integer to its hexadecimal representation (as bytes)
  base = dec_val
  hex_bytes = []
  for _ in range(num_bytes):
    item = mpc.convert(base % 2**8, secintType)
    base = base // 2**8
    hex_bytes.append(item)

  # Convert each byte to hexadecimal and then to ASCII values
  hex_ascii_array = []
  for byte in hex_bytes:
    a = byte // 16
    b = byte % 16
    a = get_ascii_code(a)
    b = get_ascii_code(b)
    hex_ascii_array.extend([b, a])

  hex_ascii_array = hex_ascii_array[::-1]

  # remove leading 0s
  while await mpc.eq_public(hex_ascii_array[0], 48):
    hex_ascii_array.pop(0)

  # Convert hex ASCII array to bits
  bits_array = []
  # for b in seclist(hex_ascii_array, secint16):
  for b in seclist(hex_ascii_array, secintType):
    for _ in range(8):
      v = b % 2
      b = b // 2
      bits_array.append(v)
  bits_array = mpc.np_fromlist(bits_array)

  hex_ascii_array = mpc.np_fromlist(hex_ascii_array)

  # NOTE: Does not work!
  # bits_array = [mpc.convert(s, secfld1) for s in bits_array]
  # x = mpc.np_fromlist(bits_array)

  # NOTE: Does not work!
  # bits_array = await mpc.gather(bits_array)
  # # bits_array = bits_array.copy()
  # bits_array = [mpc.convert(b, secfld1) for b in seclist(bits_array, secintType)]
  # x = mpc.np_fromlist(bits_array)

  # NOTE: Works!
  # TODO: However, try another way w/o revealing the secure value bits
  # bits_array = [mpc.convert(s, secint16) for s in bits_array]
  x = secfld1.array(await mpc.output(bits_array))

  # NOTE: From sha3.py
  # int_val = await mpc.output(dec_val)
  # inp_str = hex(int_val)[2:]
  # X = inp_str.encode()  # convert to bytes
  # x = np.array([(b >> i) & 1 for b in X for i in range(8)])  # bytes to bits
  # x = secfld1.array(x)  # secret-shared input bits

  # Compute sha3-256 hash
  hash = await sha3_256_hash_bits(x)

  return hash

async def create_shares():
  secret = get_nbit_rand(secint, 8 * KEY_SIZE)
  shares = shamir_split(secret, threshold, n_parties)

  # get hex hash commitments
  commitments = []
  for share in shares:
    hash = await get_hex_commitment(share)
    commitments.append(hash)

  if (len(commitments) != len(shares)):
    raise Exception(f'[Unexpected] {len(commitments)} {len(shares)}')

  return (shares, commitments)

async def reconstruct_secret(shares, commitments):
  random_numbers = mpc.random.sample(mpc.SecInt(8), range(n_parties), threshold)
  indices = await mpc.output(random_numbers)

  subset_of_shares = [shares[idx] for idx in indices]
  secret = shamir_reconstruct(subset_of_shares, indices)
  return secret

async def main():
  await mpc.start()

  num_parties = len(mpc.parties)

  if num_parties != 4:
    print('[ERROR] Script requires 4 parties!')
    sys.exit(1)

  # -----------------------------

  # create secret shares
  (shares, commitments) = await create_shares()

  outputs = [
    None,
    await mpc.output(shares[0], receivers=1),
    await mpc.output(shares[1], receivers=2),
    await mpc.output(shares[2], receivers=3),
  ]

  secret_share = outputs[mpc.pid]
  if (secret_share is not None):
    secret_share = hex(secret_share)[2:]
  print('\nsecret_share:', secret_share)

  if mpc.pid == 0:
    print('commitments:', np.array(commitments))
  else:
    print('commitment:', commitments[mpc.pid-1])
  
  # -----------------------------

  secret_share = 0
  commitment1 = 0
  commitment2 = 0
  commitment3 = 0

  if (mpc.pid == 0):
    commitment1 = int(input('\ncommitment [1]: '), 16)
    commitment2 = int(input('commitment [2]: '), 16)
    commitment3 = int(input('commitment [3]: '), 16)
  else:
    secret_share = int(input('\nsecret_share: '), 16)

  shares = mpc.input(secint(secret_share), senders=[1,2,3])
  commitments = mpc.input([secint(commitment1), secint(commitment2), secint(commitment3)], senders=0)

  # TODO: verify hex hash commitments

  # reconstruct secret
  reconstructed_secret = await reconstruct_secret(shares, commitments)

  # ideally, there should be no receivers, i.e. secret is never in plain
  secret = await mpc.output(reconstructed_secret, receivers=0)
  print('\nsecret:', hex(secret)[2:] if secret else None)

  # -----------------------------

  await mpc.shutdown()

if __name__ == '__main__':
  # try:
  mpc.run(main())
  # except:
  #   print('Exception at root')
