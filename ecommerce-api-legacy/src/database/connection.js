const sqlite3 = require('sqlite3');

// Envolve a API de callbacks do sqlite3 em Promises.
function createDatabase(filename) {
    const raw = new sqlite3.Database(filename);
    let transactionQueue = Promise.resolve();

    const db = {
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },

        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },

        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.run(sql, params, function (err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },

        // A conexão é única, então as transações são enfileiradas para não se misturarem.
        transaction(work) {
            const result = transactionQueue.then(async () => {
                await db.run('BEGIN');
                try {
                    const value = await work();
                    await db.run('COMMIT');
                    return value;
                } catch (err) {
                    await db.run('ROLLBACK');
                    throw err;
                }
            });
            transactionQueue = result.catch(() => {});
            return result;
        },

        close() {
            return new Promise((resolve, reject) => {
                raw.close((err) => (err ? reject(err) : resolve()));
            });
        }
    };

    return db;
}

module.exports = { createDatabase };
