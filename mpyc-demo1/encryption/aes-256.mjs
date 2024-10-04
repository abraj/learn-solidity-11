import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

const KEY = '0c0daf375367a2f14eadc080b0864dfb8c976cf1a7effb637503dc7cbaf9164e'
const IV = '122d18127cc2775be9b2cfec86ec2135'

const message = 'i like turtles';
const key = Buffer.from(KEY, 'hex');
const iv = Buffer.from(IV, 'hex');
// const key = randomBytes(32);
// const iv = randomBytes(16);

const algorithm = 'aes-256-cbc';
const cipher = createCipheriv(algorithm, key, iv);
const encrypted = cipher.update(message, 'utf-8', 'hex') + cipher.final('hex');

const decipher = createDecipheriv(algorithm, key, iv);
const decrypted = decipher.update(encrypted, 'hex', 'utf-8') + decipher.final('utf-8');

console.log('>>>', message);
console.log('>>>', encrypted);
console.log('>>>', decrypted);
