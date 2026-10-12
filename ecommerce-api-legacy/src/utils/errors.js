class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

class BadRequestError extends AppError {
    constructor(message = 'Bad Request') {
        super(400, message);
    }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Não autorizado') {
        super(401, message);
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Não encontrado') {
        super(404, message);
    }
}

module.exports = { AppError, BadRequestError, UnauthorizedError, NotFoundError };
