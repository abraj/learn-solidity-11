import numpy as np

def pad_str(str):
  """
  Pads an ascii string with invisible characters
    len('Hello, World!') == 13
    len(pad_str('Hello, World!')) == 16
  """
  block_size = 16  # AES block size: 16 bytes (128 bits)
  if not str.isascii():
    print('[WARN] Non-ascii string:', str)
    str = ''.join([(char if char.isascii() else '?') for char in str])
  padding = block_size - (len(str) % block_size)
  padded_text = str + chr(padding) * padding
  return padded_text

def unpad_str(padded_str):
  """
  Removes padding for a (padded) ascii string
    padded_str = pad_str('Hello, World!')
    len(padded_str) == 16
    len(unpad_str(padded_str)) == 13
  """
  block_size = 16  # AES block size in bytes
  if (len(padded_str) > 0 and len(padded_str) % block_size != 0):
    print(f'[ERROR] Provided string must be padded ({block_size} bytes): [{len(padded_str)}] {padded_str}')
    return None
  last_char = padded_str[len(padded_str)-1]
  padding = ord(last_char)
  return padded_str[:-1*padding]

def str_to_bytes(str):
  """
  Converts an ascii string to (ascii) bytes array
    str_to_bytes('Hello') == [72, 101, 108, 108, 111]
  """
  ascii_size = 2 ** 7  # 128 (0-127)
  if not str.isascii():
    print('[WARN] Non-ascii string:', str)
    bytes_array = [(ord(char) if ord(char) < ascii_size else ord('?')) for char in str]
  else:
    bytes_array = [ord(char) for char in str]
  return bytes_array

def str_from_bytes(bytes_array):
  """
  Converts an (ascii) bytes array to ascii string
    str_from_bytes([72, 101, 108, 108, 111]) == 'Hello'
  """
  ascii_size = 2 ** 7  # 128 (0-127)
  non_ascii_bytes = list(filter(lambda b: b >= ascii_size, bytes_array))
  non_ascii_chars = [chr(byte) for byte in non_ascii_bytes]
  if len(non_ascii_chars) > 0:
    print('[WARN] Non-ascii characters found:', non_ascii_chars, non_ascii_bytes)
    chars_array = [(chr(byte) if byte < ascii_size else '?') for byte in bytes_array]
  else:
    chars_array = [chr(byte) for byte in bytes_array]
  return ''.join(chars_array)

def hex_to_bytes(hex_str):
  """
  Converts a hex string to bytes array
    hex_to_bytes('48656c6c6f') == [72, 101, 108, 108, 111]
  """
  bytearray_obj = bytearray.fromhex(hex_str)
  bytes_array = [byte for byte in bytearray_obj]
  return bytes_array

def hex_from_bytes(bytes_array):
  """
  Converts a bytes array to hex string
    hex_from_bytes([72, 101, 108, 108, 111]) == '48656c6c6f'
  """
  bytearray = bytes(bytes_array)
  hex_str = bytearray.hex()
  return hex_str

def str_to_hex(str):
  """
  Converts an ascii string to hex string
    str_to_hex('Hello, World!') == '48656c6c6f2c20576f726c6421'
  """
  bytes_array = str_to_bytes(str)
  hex_str = hex_from_bytes(bytes_array)
  return hex_str

def str_from_hex(hex_str):
  """
  Converts a hex string to ascii string
    str_from_hex('48656c6c6f2c20576f726c6421') == 'Hello, World!'
  """
  bytes_array = hex_to_bytes(hex_str)
  str = str_from_bytes(bytes_array)
  return str

def padhex_str(str):
  """
  Pads an ascii string, and then converts it to a hex string
    str_to_hex('Hello, World!') == '48656c6c6f2c20576f726c6421'
    padhex_str('Hello, World!') == '48656c6c6f2c20576f726c6421030303'
  """
  padded_text = pad_str(str)
  return str_to_hex(padded_text)

def unpadhex_str(hex_str):
  """
  Converts a (padded) hex string to an (unpadded) ascii string
    str_from_hex('48656c6c6f2c20576f726c6421') == 'Hello, World!'
    len(str_from_hex('48656c6c6f2c20576f726c6421030303')) == 16
    len(unpadhex_str('48656c6c6f2c20576f726c6421030303')) == 13
  """
  block_size = 16  # AES block size in bytes
  if len(hex_str) % (2 * block_size) != 0:
    print(f'[ERROR] Provided hex_str must be padded ({block_size} bytes): [{len(hex_str)}] {hex_str}')
    return None
  padded_text = str_from_hex(hex_str)
  return unpad_str(padded_text)

def create_matrix(bytes_array):
  matrix = np.zeros((4, 4), dtype=np.uint8)
  for i in range(4):
    for j in range(4):
      index = i + j * 4
      if index < len(bytes_array):
        matrix[i][j] = bytes_array[index]
      else:
        matrix[i][j] = 0  # Fill with zero if no more data
  return matrix

def prepare_for_aes(plaintext):
  padded_text = pad_str(plaintext)
  bytes_array = str_to_bytes(padded_text)
  block_data = create_matrix(bytes_array)
  return block_data

# Example usage:
# plaintext = ""
# plaintext = "Hello"
# plaintext = "Hello, World!"
# plaintext = "Hello, xxyWorld!"
# plaintext = "Hello, xxyzWorld!"
# plaintext = "H€llo, World!"
# aes_input = prepare_for_aes(plaintext)
# print(aes_input)
