const { AppError } = require('../utils/errors');

const INTERNAL_ERROR_MESSAGE = 'Erro interno. Tente novamente.';

// Respostas de erro continuam em texto puro, como no contrato original.
function errorHandler(err, req, res, next) {
    if (res.headersSent) return next(err);

    if (err instanceof AppError) {
        return res.status(err.status).send(err.message);
    }
    // Erros do body-parser (JSON inválido, payload grande demais) já trazem um status 4xx.
    if (err.status >= 400 && err.status < 500) {
        return res.status(err.status).send('Bad Request');
    }

    console.error(err);
    res.status(500).send(INTERNAL_ERROR_MESSAGE);
}

module.exports = errorHandler;
