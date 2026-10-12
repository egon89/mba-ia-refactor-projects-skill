function createPaymentModel(db) {
    return {
        create({ enrollmentId, amount, status }) {
            return db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrollmentId, amount, status]);
        },

        deleteByUserId(userId) {
            return db.run(
                "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
                [userId]
            );
        }
    };
}

module.exports = { createPaymentModel };
