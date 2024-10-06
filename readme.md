## MPC: Multi-party computation

- https://sands.edpsciences.org/articles/sands/full_html/2022/01/sands20210001/sands20210001.html

## MPC libraries

- https://chatgpt.com/c/66fc8557-ac9c-8006-816b-d45a94c7ae07

## MPyC

- https://github.com/lschoe/mpyc
- https://chatgpt.com/c/670160d9-2bdc-8006-9f02-c560ee7ef303
- https://mpyc.readthedocs.io/en/latest/mpyc.html
- https://mpyc.readthedocs.io/en/latest/demos.html
- https://www.youtube.com/watch?v=bSC4rCHbLlc
- https://pure.tue.nl/ws/portalfiles/portal/333714970/Gils_N.pdf

## Online tools

- https://emn178.github.io/online-tools/sha3_256.html

## Roadmap

```
[private keys + public/private key pairs]
 1 trusted party
 3 storage parties

[mappings]
 user/trusted party mapping (explicit)
 user/storage party mappings (implicit)

[Auth]
 user completes MFA w/ trusted party on site

setup shamir secret: (2/3)
 [*] create a "secure" random key
 [*] split the key into 3 shares
 [*] reveal a key share to the "specific" party only
 [ ] a storage party stores the encrypted version of its share in its smart contract

encrypt:
 trusted party gets user input as plaintext
 get plaintext as "secure" input (from trusted party)
 get keys shares from all 3 parties as "hex string" secure input
 pick 2 shares from them at random
 reconstruct the key from the 2 shares
 output: ciphertext
 TODO: return encypted ciphertext w.r.t. trusted party
 ciphertext is stored in smart contract by trusted party (on behalf of user)

decrypt:
 trusted party reads ciphertext from smart contract (on behalf of user)
 get ciphertext as "secure" input (from trusted party)
 get keys shares from all 3 parties as "hex string" input
 pick 2 shares from them at random
 reconstruct the key from the 2 shares
 output: plaintext
 TODO: return encypted plaintext w.r.t. trusted party
 trusted party shows the plaintext on user site
```
