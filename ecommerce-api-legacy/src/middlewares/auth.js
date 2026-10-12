const crypto = require('crypto');
const { UnauthorizedError } = require('../utils/errors');

const BEARER_PREFIX = 'Bearer ';

function safeEqual(a, b) {
    const digestA = crypto.createHash('sha256').update(a).digest();
    const digestB = crypto.createHash('sha256').update(b).digest();
    return crypto.timingSafeEqual(digestA, digestB);
}

// Exige "Authorization: Bearer <ADMIN_API_TOKEN>". Sem token configurado, nega tudo.
function createRequireAdmin({ adminApiToken }) {
    return (req, res, next) => {
        const header = req.headers.authorization || '';
        const token = header.startsWith(BEARER_PREFIX) ? header.slice(BEARER_PREFIX.length) : '';

        if (!adminApiToken || !token || !safeEqual(token, adminApiToken)) {
            return next(new UnauthorizedError());
        }
        next();
    };
}

module.exports = { createRequireAdmin };
