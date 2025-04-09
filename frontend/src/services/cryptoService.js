export default {
  decryptWithKMS(encryptedData) {
    // Mock decryption logic
    return `Decrypted(${encryptedData})`
  },
  generateHMAC(data, secret) {
    // Mock HMAC generation logic
    return `HMAC(${data}, ${secret})`
  },
  generateSHA256(data) {
    // Mock SHA-256 hash generation logic
    return `SHA256(${data})`
  }
}