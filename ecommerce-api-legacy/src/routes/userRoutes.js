const express = require('express');
const asyncHandler = require('../utils/asyncHandler');

function createUserRoutes({ userController, requireAdmin }) {
    const router = express.Router();
    router.delete('/api/users/:id', requireAdmin, asyncHandler(userController.remove));
    return router;
}

module.exports = { createUserRoutes };
