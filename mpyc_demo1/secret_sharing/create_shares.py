import sys
# import numpy as np
from mpyc.runtime import mpc
from shamir import shamir_split, shamir_reconstruct
from utils.mpc_utils import get_nbit_rand

secint = mpc.SecInt(257)

async def main():
  await mpc.start()

  KEY_SIZE = 32  # 32 bytes (256 bits)
  num_parties = len(mpc.parties)

  if num_parties != 4:
    print('[ERROR] Script requires 4 parties!')
    sys.exit(1)

  secret = get_nbit_rand(secint, 8 * KEY_SIZE)

  threshold = 2            # Minimum number of shares required for reconstruction
  n_parties = 3            # Total number of parties
  shares = shamir_split(secret, threshold, n_parties)

  outputs = [
    None,
    await mpc.output(shares[0], receivers=1),
    await mpc.output(shares[1], receivers=2),
    await mpc.output(shares[2], receivers=3),
  ]
  secret_share = outputs[mpc.pid]
  print(secret_share)

  # print(shares)
  # print(np.array(await mpc.output(shares)))

  # indices = [i for i in range(threshold)]
  # subset_of_shares = [shares[idx] for idx in indices]

  # reconstructed_secret = shamir_reconstruct(subset_of_shares, indices)
  # print(await mpc.output(reconstructed_secret))

  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
