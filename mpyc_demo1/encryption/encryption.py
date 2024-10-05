import sys
import numpy as np
from mpyc.runtime import mpc
from utils.utils import prepare_for_aes
from secret_sharing.shares import reconstruct_secret

secint = mpc.SecInt(257)
secfld = mpc.SecFld(2**8)  # Secure AES field GF(2^8) for secret values.
f256 = secfld.field        # Plain AES field GF(2^8) for public values.

async def main():
  await mpc.start()

  num_parties = len(mpc.parties)

  if num_parties != 4:
    print('[ERROR] Script requires 4 parties!')
    sys.exit(1)
 
  if (mpc.pid == 0):
    text = input('Enter plain text: ')
    block_data = prepare_for_aes(text)
  else:
    block_data = np.zeros((4, 4), dtype=np.uint8)
 
  if (mpc.pid == 0):
    share = 0
  else:
    user_inp = input('Enter secret share: ')
    share = int(user_inp, 16)

  plaintext = mpc.input(secfld.array(f256.array(block_data)), senders=0)
  shares = mpc.input(secint(share), senders=[1, 2, 3])

  # print(plaintext)
  # print(shares)
  # print(await mpc.output(plaintext))
  # print(await mpc.output(shares))

  secret = await reconstruct_secret(shares)
  # print(secret)
  # print(await mpc.output(secret))

  print(plaintext)
  print(secret)
  print(await mpc.output(secret))

  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
