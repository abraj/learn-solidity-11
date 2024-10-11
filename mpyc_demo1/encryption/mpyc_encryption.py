import sys
import numpy as np
from mpyc.runtime import mpc
from utils.utils import prepare_for_aes, str_from_bytes, unpad_str
from utils.mpc_utils import random_bytes, prepare_aes_key, secint_to_secfld, mpc_pack
from secret_sharing.shares import reconstruct_secret, verify_shares
from encryption.np_aes_plus import aes_256_encrypyt, aes_256_decrypyt

secint = mpc.SecInt(257)
secint16 = mpc.SecInt(16)
secfld = mpc.SecFld(2**8)  # Secure AES field GF(2^8) for secret values.
f256 = secfld.field        # Plain AES field GF(2^8) for public values.

async def xprint(text, s):
  """Print matrix s transposed and flattened as hex string."""
  s = list(map(list, zip(*s)))
  s = await mpc.output(sum(s, []))
  print(f'{text} ({len(s)}) {bytes(map(int, s)).hex()}')

async def block_bytes(s):
  """Get bytes from (transposed and flattened) matrix s"""
  s = list(map(list, zip(*s)))
  s = await mpc.output(sum(s, []))
  s = list(map(int, s))
  return s

async def xprint2(text, s, hex=False):
  """Print matrix s transposed and flattened as ASCII string."""
  block_bytes_arr = [byte for block in s for byte in await block_bytes(block)]
  if hex:
    s = bytes(block_bytes_arr).hex()
    length = len(block_bytes_arr)
  else:
    s = str_from_bytes(block_bytes_arr)
    s = unpad_str(s)
    length = len(s)
  print(f'{text} ({length}) {s}')

async def main():
  await mpc.start()

  num_parties = len(mpc.parties)

  if num_parties != 4:
    print('[ERROR] Script requires 4 parties!')
    sys.exit(1)
  
  secret_share = 0
  commitment1 = 0
  commitment2 = 0
  commitment3 = 0
 
  if (mpc.pid == 0):
    text = input('Enter plain text: ')
    block_data = prepare_for_aes(text)
    commitment1 = int(input('\ncommitment [1]: '), 16)
    commitment2 = int(input('commitment [2]: '), 16)
    commitment3 = int(input('commitment [3]: '), 16)
  else:
    user_inp = input('Enter secret share: ')
    secret_share = int(user_inp, 16)
    block_data = np.zeros((1, 4, 4), dtype=np.uint8)

  dims = await mpc.transfer(block_data.shape, senders=[0], receivers=[1,2,3])
  if (mpc.pid != 0):
    block_shape = dims[0]
    block_data = np.zeros(block_shape, dtype=np.uint8)

  block_data = secfld.array(f256.array(block_data))
  plaintext = mpc.input(block_data, senders=0)

  rand_bytes = await random_bytes(16)
  iv = [[rand_bytes[(4*j + i)] for j in range(4)] for i in range(4)]
  iv = secfld.array(f256.array(iv))

  shares = mpc.input(secint(secret_share), senders=[1, 2, 3])

  commitments = mpc.input([secint(commitment1), secint(commitment2), secint(commitment3)], senders=0)
  commitments = await mpc.output(commitments)

  # verify hex hash commitments
  verified_shares = await verify_shares(shares, commitments)

  # reconstruct secret
  secret = await reconstruct_secret(verified_shares)

  # prepare AES key
  secret_block_32bytes = prepare_aes_key(secret)

  encryption_key = np.zeros((4, 8), dtype=object)
  for i in range(4):
    for j in range(8):
      encryption_key[i][j] = await secint_to_secfld(secret_block_32bytes[i][j], secint16)
  encryption_key = mpc_pack(encryption_key)

  # AES-256 encrypt
  ciphertext = aes_256_encrypyt(encryption_key, iv, plaintext)

  # AES-256 decrypt
  plaintext2 = aes_256_decrypyt(encryption_key, iv, ciphertext)

  await xprint2(f'\nPlaintext:  ', plaintext, hex=True)
  await xprint(f'AES-256 key:', encryption_key)
  await xprint(f'AES-256 IV: ', iv)
  await xprint2('Ciphertext: ', ciphertext, hex=True)

  await xprint2('\nPlaintext:  ', plaintext2)

  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
