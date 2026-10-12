const { BadRequestError } = require('../utils/errors');

const isFilledString = (value) => typeof value === 'string' && value.length > 0;

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body || {};

            const validPassword = password === undefined || password === null || typeof password === 'string';
            if (!isFilledString(name) || !isFilledString(email) || !isFilledString(cardNumber) || !courseId || !validPassword) {
                throw new BadRequestError();
            }

            const { enrollmentId } = await checkoutService.checkout({ name, email, password, courseId, cardNumber });
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        }
    };
}

module.exports = { createCheckoutController };
