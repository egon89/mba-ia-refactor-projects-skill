const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/businessRules');

// Gateway simulado. Uma integração real usaria gatewayKey; ela nunca deve ser logada.
function createPaymentService({ gatewayKey }) {
    return {
        authorize(cardNumber) {
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        }
    };
}

module.exports = { createPaymentService };
