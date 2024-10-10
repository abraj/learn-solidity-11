import sys
import numpy as np
from mpyc.runtime import mpc
from utils.utils import prepare_for_aes, prepare_aes_key, str_from_bytes
from secret_sharing.shares import reconstruct_secret, verify_shares
from encryption.np_aes_plus import aes_256_encrypyt, aes_256_decrypyt

secint = mpc.SecInt(257)
secfld = mpc.SecFld(2**8)  # Secure AES field GF(2^8) for secret values.
f256 = secfld.field        # Plain AES field GF(2^8) for public values.

async def xprint(text, s):
    """Print matrix s transposed and flattened as hex string."""
    s = list(map(list, zip(*s)))
    s = await mpc.output(sum(s, []))
    print(f'{text} {bytes(map(int, s)).hex()}')

async def xprint2(text, s):
    """Print matrix s transposed and flattened as hex string."""
    s = list(map(list, zip(*s)))
    s = await mpc.output(sum(s, []))
    t = list(map(int, s))
    print(f'{text} {str_from_bytes(t)}')

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
    block_data = np.zeros((4, 4), dtype=np.uint8)

  # TODO: Add support for multi-block data

  block_data = secfld.array(f256.array(block_data))
  plaintext = mpc.input(block_data, senders=0)

  shares = mpc.input(secint(secret_share), senders=[1, 2, 3])

  commitments = mpc.input([secint(commitment1), secint(commitment2), secint(commitment3)], senders=0)
  commitments = await mpc.output(commitments)

  # verify hex hash commitments
  verified_shares = await verify_shares(shares, commitments)

  # reconstruct secret
  secret = await reconstruct_secret(verified_shares)

  # prepare AES key
  secret_block_32bytes = prepare_aes_key(secret)

  # TODO: Avoid the intermediate reveal step
  # secret_block_32bytes = mpc.convert(secret_block_32bytes, secfld)
  encryption_key = np.zeros((4, 8), dtype=object)
  for i in range(4):
    for j in range(8):
      encryption_key[i][j] = await mpc.output(secret_block_32bytes[i][j])
  encryption_key = secfld.array(f256.array(encryption_key))

  # AES-256 encrypt
  ciphertext = aes_256_encrypyt(encryption_key, plaintext)

  # AES-256 decrypt
  plaintext2 = aes_256_decrypyt(encryption_key, ciphertext)

  # await xprint('Plaintext:  ', plaintext)
  # await xprint('AES-256 key:', encryption_key)
  # await xprint('Ciphertext: ', ciphertext)
  await xprint2('Plaintext:', plaintext2)

  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
