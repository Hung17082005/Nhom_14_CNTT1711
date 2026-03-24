from odoo import models, fields, api
from datetime import datetime


class PayslipWizard(models.TransientModel):
    """Wizard to create payslips in bulk for all employees in a month"""
    _name = 'payslip.wizard'
    _description = 'Wizard Tạo Phiếu Lương Hàng Loạt'

    month = fields.Char(
        string='Tháng',
        required=True,
        default=lambda self: datetime.now().strftime('%Y-%m'),
        help='Format: YYYY-MM'
    )

    employee_ids = fields.Many2many(
        'hr.employee',
        string='Nhân Viên',
        help='Leave empty to create for all active employees'
    )

    note = fields.Text(string='Ghi Chú')

    def action_create_payslips(self):
        """Create payslips for selected employees"""
        BangLuong = self.env['bang.luong']

        # Get employees
        if self.employee_ids:
            employees = self.employee_ids
        else:
            # All active employees
            employees = self.env['hr.employee'].search([('active', '=', True)])

        # Create payslips
        created_count = 0
        for employee in employees:
            # Check if already exists
            existing = BangLuong.search([
                ('employee_id', '=', employee.id),
                ('month', '=', self.month),
            ])

            if not existing:
                payslip = BangLuong.create({
                    'employee_id': employee.id,
                    'month': self.month,
                    'notes': self.note,
                })
                payslip.action_generate_lines()
                created_count += 1

        message = f"Đã tạo {created_count} phiếu lương cho tháng {self.month}"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành Công',
                'message': message,
                'sticky': False,
            }
        }
