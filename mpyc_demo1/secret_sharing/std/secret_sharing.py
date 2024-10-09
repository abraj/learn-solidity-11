from secretsharing import PlaintextToHexSecretSharer
from secretsharing import SecretSharer

def is_hex(s):
  try:
    int(s, 16)
    return True
  except ValueError:
    return False

def main():
  # secret = "This is a secret message"
  secret = "c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a"

  num_shares = 5   # Total number of shares to create
  threshold = 3    # Minimum shares needed to reconstruct the secret

  # secretSharer = PlaintextToHexSecretSharer  # Plaintext Secrets
  secretSharer = SecretSharer  # Hex Secrets
  hex_switch_reqd = not is_hex(secret)

  print(f"Original secret: '{secret}'")

  if hex_switch_reqd:
    secret = secret.encode().hex()

  # Create shares
  shares = secretSharer.split_secret(secret, threshold, num_shares)
  print("\nShares created:")
  for share in shares:
      print(share)

  secret_shares = shares[:threshold]

  # Reconstruct the secret from the shares
  reconstructed_secret = secretSharer.recover_secret(secret_shares)

  if hex_switch_reqd:
    reconstructed_secret = bytes.fromhex(reconstructed_secret).decode()

  print(f"\nReconstructed secret: '{reconstructed_secret}'")

if __name__ == "__main__":
  main()
