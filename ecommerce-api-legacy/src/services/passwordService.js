const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);

const SALT_BYTES = 16;
const KEY_BYTES = 64;
const SCHEME = 'scrypt';

async function hash(password) {
    const salt = crypto.randomBytes(SALT_BYTES);
    const key = await scrypt(password, salt, KEY_BYTES);
    return `${SCHEME}$${salt.toString('hex')}$${key.toString('hex')}`;
}

async function verify(password, stored) {
    const [scheme, saltHex, keyHex] = String(stored).split('$');
    if (scheme !== SCHEME || !saltHex || !keyHex) return false;

    const expected = Buffer.from(keyHex, 'hex');
    const actual = await scrypt(password, Buffer.from(saltHex, 'hex'), expected.length);
    return crypto.timingSafeEqual(actual, expected);
}

module.exports = { hash, verify };
