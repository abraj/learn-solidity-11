import numpy as np

def pad_plaintext(plaintext):
    block_size = 16  # AES block size in bytes
    padding = block_size - (len(plaintext) % block_size)
    padded_text = plaintext + chr(padding) * padding
    return padded_text

def convert_to_bytes(padded_text):
    return [ord(char) for char in padded_text]

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
    padded_text = pad_plaintext(plaintext)
    bytes_array = convert_to_bytes(padded_text)
    return create_matrix(bytes_array)

# Example usage:
plaintext = "Hello, World!"
aes_input = prepare_for_aes(plaintext)
print(aes_input)
