function createUserService({ db, userModel, enrollmentModel, paymentModel, auditLogModel }) {
    return {
        // Remove o usuário junto com suas matrículas e pagamentos, para não deixar registros órfãos.
        remove(userId) {
            return db.transaction(async () => {
                await paymentModel.deleteByUserId(userId);
                await enrollmentModel.deleteByUserId(userId);
                const { changes } = await userModel.deleteById(userId);
                if (changes > 0) await auditLogModel.create(`Usuário ${userId} removido`);
                return { deleted: changes > 0 };
            });
        }
    };
}

module.exports = { createUserService };
