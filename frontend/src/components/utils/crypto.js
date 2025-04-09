import { Fernet } from 'fernet';
import { hmac } from 'crypto-js';

export const encryptMedicalData = (data, secret) => {
  const fernet = new Fernet(secret);
  return fernet.encrypt(JSON.stringify(data));
};

export const generateEmailHash = (email, key) => {
  return hmac(email, key, { algorithm: 'SHA256' }).toString();
};