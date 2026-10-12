const express = require('express');
const config = require('./config');
const { createDatabase } = require('./database/connection');
const { createSchema, seed } = require('./database/schema');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const passwordService = require('./services/passwordService');
const { createPaymentService } = require('./services/paymentService');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createCheckoutRoutes } = require('./routes/checkoutRoutes');
const { createAdminRoutes } = require('./routes/adminRoutes');
const { createUserRoutes } = require('./routes/userRoutes');
const { createRequireAdmin } = require('./middlewares/auth');
const errorHandler = require('./middlewares/errorHandler');

function createApp({ db }) {
    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);

    const paymentService = createPaymentService({ gatewayKey: config.paymentGatewayKey });
    const checkoutService = createCheckoutService({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService, passwordService
    });
    const reportService = createReportService({ courseModel });
    const userService = createUserService({ db, userModel, enrollmentModel, paymentModel, auditLogModel });

    const checkoutController = createCheckoutController({ checkoutService });
    const reportController = createReportController({ reportService });
    const userController = createUserController({ userService });
    const requireAdmin = createRequireAdmin({ adminApiToken: config.adminApiToken });

    const app = express();
    app.use(express.json());
    app.use(createCheckoutRoutes({ checkoutController }));
    app.use(createAdminRoutes({ reportController, requireAdmin }));
    app.use(createUserRoutes({ userController, requireAdmin }));
    app.use(errorHandler);
    return app;
}

async function start() {
    const db = createDatabase(config.dbFile);
    await createSchema(db);
    await seed(db, passwordService);

    if (!config.adminApiToken) {
        console.warn('ADMIN_API_TOKEN não definido: as rotas administrativas responderão 401.');
    }

    createApp({ db }).listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

if (require.main === module) {
    start().catch((err) => {
        console.error(err);
        process.exit(1);
    });
}

module.exports = { createApp };
