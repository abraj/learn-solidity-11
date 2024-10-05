import sys
import random
# import numpy as np
from mpyc.runtime import mpc
from secret_sharing.shamir import shamir_split, shamir_reconstruct
from utils.mpc_utils import get_nbit_rand

KEY_SIZE = 32  # 32 bytes (256 bits)

secint = mpc.SecInt(257)

threshold = 2            # Minimum number of shares required for reconstruction
n_parties = 3            # Total number of parties

async def create_shares():
  secret = get_nbit_rand(secint, 8 * KEY_SIZE)
  shares = shamir_split(secret, threshold, n_parties)
  return shares

async def reconstruct_secret(shares):
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

  # create secret shares
  shares = await create_shares()
  outputs = [
    None,
    await mpc.output(shares[0], receivers=1),
    await mpc.output(shares[1], receivers=2),
    await mpc.output(shares[2], receivers=3),
  ]
  secret_share = outputs[mpc.pid]
  print('secret_share:', hex(secret_share)[2:] if secret_share else None)

  # reconstruct secret
  reconstructed_secret = await reconstruct_secret(shares)
  secret = await mpc.output(reconstructed_secret, receivers=0)
  # ideally, there should be no receivers, i.e. secret is never in plain
  print('secret:', hex(secret)[2:] if secret else None)

  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
