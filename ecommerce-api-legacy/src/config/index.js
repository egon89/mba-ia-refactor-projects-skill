// Carrega .env quando existir (Node >= 21.7); em produção as variáveis vêm do ambiente.
if (typeof process.loadEnvFile === 'function') {
    try {
        process.loadEnvFile();
    } catch (err) {
        if (err.code !== 'ENOENT') throw err;
    }
}

const DEFAULT_PORT = 3000;

const config = {
    port: Number(process.env.PORT) || DEFAULT_PORT,
    dbFile: process.env.DB_FILE || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || null,
    adminApiToken: process.env.ADMIN_API_TOKEN || null
};

module.exports = config;
