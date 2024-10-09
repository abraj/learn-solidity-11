function padPlaintext(plaintext) {
  const blockSize = 16; // AES block size in bytes
  const padding = blockSize - (plaintext.length % blockSize);
  const paddedText = plaintext + String.fromCharCode(padding).repeat(padding);
  return paddedText;
}

function convertToBytes(paddedText) {
  const bytes = new Uint8Array(paddedText.length);
  for (let i = 0; i < paddedText.length; i++) {
    bytes[i] = paddedText.charCodeAt(i);
  }
  return bytes;
}

function createMatrix(bytes) {
  const matrix = [];
  for (let i = 0; i < 4; i++) {
    const row = [];
    for (let j = 0; j < 4; j++) {
      row.push(bytes[i + j * 4]);
    }
    matrix.push(row);
  }
  return matrix;
}

function prepareForAES(plaintext) {
  const paddedText = padPlaintext(plaintext);
  const bytes = convertToBytes(paddedText);
  return createMatrix(bytes);
}

// Example usage:
const plaintext = 'Hello, World!';
const aesInput = prepareForAES(plaintext);
console.log(aesInput);
