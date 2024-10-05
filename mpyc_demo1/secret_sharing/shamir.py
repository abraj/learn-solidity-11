from mpyc.runtime import mpc
from utils.mpc_utils import get_nbit_rand

# secint = mpc.SecInt(31)  # Mersenne prime (2^31 - 1) [Does not work with large (> 2^60) integers]
secint = mpc.SecInt(257)

def shamir_split(secret, threshold, n):
  """Split secret using Shamir's Secret Sharing into n shares with threshold."""

  # Generate random coefficients for a polynomial of degree `threshold - 1`
  coeffs = [secret] + [get_nbit_rand(secint, 256) for _ in range(threshold - 1)]

  shares = []
  for i in range(1, n + 1):  # i is the party ID or index
    # Evaluate the polynomial at x = i (for each party)
    share = sum(c * (i ** idx) for idx, c in enumerate(coeffs))
    shares.append(share)
  return shares

def shamir_reconstruct(shares, indices):
  """Reconstruct the secret from shares using Lagrange interpolation."""

  if (len(shares) != len(indices) or len(indices) == 0):
    raise Exception(f'Invalid args type/len: {len(shares)} {len(indices)}')

  typeName = type(shares[0]).__name__
  if (not typeName.startswith('SecInt') or len(typeName) <= len('SecInt')):
    raise Exception(f'Invalid share type: {typeName}')

  secintSize = int(typeName[len('Secint'):])
  secint0 = mpc.SecInt(secintSize)

  x_values = [secint0(idx + 1) for idx in indices]
  secret = 0
  for i in range(len(shares)):
    # Compute the Lagrange coefficient for share i
    lagrange_coeff = 1
    for j in range(len(shares)):
      if i != j:
        lagrange_coeff *= (x_values[j] / (x_values[j] - x_values[i]))
    secret += shares[i] * lagrange_coeff
  return secret

async def main():
  await mpc.start()
  
  # secret_int = 12345
  # secret_hex = '47f047f047f047f' # 60 bits
  # secret_hex = '47f047f047f047f2' # 64 bits
  secret_hex = '47f047f047f047f047f047f047f047f047f047f047f047f047f047f047f047f0' # 256 bits (32 bytes)
  secret_int = int(secret_hex, 16)
  print('-->', secret_int)

  # Parameters
  secret = secint(secret_int)   # Secret to be shared
  threshold = 2            # Minimum number of shares required for reconstruction
  n_parties = 3            # Total number of parties

  # Split secret into shares
  shares = shamir_split(secret, threshold, n_parties)

  # Reconstruct the secret using a subset of shares (at least `threshold` shares needed)
  indices = [i for i in range(threshold)]
  # indices = [0, 1, 2]
  # indices = [1, 2, 3]
  # indices = [0, 3, 4]
  subset_of_shares = [shares[idx] for idx in indices]

  reconstructed_secret = shamir_reconstruct(subset_of_shares, indices)

  # Output the reconstructed secret
  reconstructed_secret = await mpc.output(reconstructed_secret)
  print('==>', reconstructed_secret)

  await mpc.shutdown()

if __name__ == "__main__":
  mpc.run(main())
