const { PAYMENT_STATUS } = require('../config/businessRules');

const UNKNOWN_STUDENT = 'Unknown';

function createReportService({ courseModel }) {
    return {
        async financialReport() {
            const rows = await courseModel.findAllWithEnrollments();
            const byCourse = new Map();

            for (const row of rows) {
                if (!byCourse.has(row.course_id)) {
                    byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue;

                const courseData = byCourse.get(row.course_id);
                if (row.payment_status === PAYMENT_STATUS.PAID) {
                    courseData.revenue += row.payment_amount;
                }
                courseData.students.push({
                    student: row.student_name || UNKNOWN_STUDENT,
                    paid: row.payment_amount || 0
                });
            }

            return [...byCourse.values()];
        }
    };
}

module.exports = { createReportService };
