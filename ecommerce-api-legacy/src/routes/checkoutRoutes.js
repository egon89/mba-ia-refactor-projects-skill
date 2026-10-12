const express = require('express');
const asyncHandler = require('../utils/asyncHandler');

function createCheckoutRoutes({ checkoutController }) {
    const router = express.Router();
    router.post('/api/checkout', asyncHandler(checkoutController.checkout));
    return router;
}

module.exports = { createCheckoutRoutes };
