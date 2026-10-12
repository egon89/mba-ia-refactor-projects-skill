const { PAYMENT_STATUS } = require('../config/businessRules');
const { BadRequestError, NotFoundError } = require('../utils/errors');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService, passwordService }) {
    return {
        async checkout({ name, email, password, courseId, cardNumber }) {
            const course = await courseModel.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            const existingUser = await userModel.findByEmail(email);
            if (!existingUser && !password) throw new BadRequestError();

            const paymentStatus = paymentService.authorize(cardNumber);
            if (paymentStatus === PAYMENT_STATUS.DENIED) throw new BadRequestError('Pagamento recusado');

            const passwordHash = existingUser ? null : await passwordService.hash(password);

            return db.transaction(async () => {
                // Reconsulta dentro da transação: outro checkout pode ter criado o mesmo e-mail nesse intervalo.
                const currentUser = existingUser || await userModel.findByEmail(email);
                const userId = currentUser
                    ? currentUser.id
                    : await userModel.create({ name, email, passwordHash });

                const enrollmentId = await enrollmentModel.create({ userId, courseId });
                await paymentModel.create({ enrollmentId, amount: course.price, status: paymentStatus });
                await auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);

                return { enrollmentId };
            });
        }
    };
}

module.exports = { createCheckoutService };
