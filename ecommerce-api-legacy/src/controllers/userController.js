function createUserController({ userService }) {
    return {
        async remove(req, res) {
            await userService.remove(req.params.id);
            res.send('Usuário deletado junto com suas matrículas e pagamentos.');
        }
    };
}

module.exports = { createUserController };
