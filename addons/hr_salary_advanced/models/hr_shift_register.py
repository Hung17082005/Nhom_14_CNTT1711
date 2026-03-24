from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class HrShiftRegister(models.Model):
    """Model for registering shifts per month"""
    _name = 'hr.shift.register'
    _description = 'Ca Làm Việc Theo Tháng'
    _order = 'month desc, employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
        ondelete='cascade'
    )

    month = fields.Char(
        string='Tháng',
        required=True,
        help='Format: YYYY-MM'
    )

    shift_ids = fields.One2many(
        'hr.shift.detail',
        'register_id',
        string='Chi Tiết Ca Làm',
        copy=True
    )

    state = fields.Selection(
        [('draft', 'Bản Nháp'), ('submitted', 'Đã Gửi'), ('approved', 'Đã Duyệt')],
        string='Trạng Thái',
        default='draft',
        track_visibility='onchange'
    )

    total_days = fields.Integer(
        string='Tổng Ngày Làm',
        compute='_compute_total_days',
        store=True
    )

    @api.depends('shift_ids.shift_type')
    def _compute_total_days(self):
        """Count working days (exclude 'off' shifts)"""
        for record in self:
            record.total_days = len([s for s in record.shift_ids if s.shift_type != 'off'])

    def action_submit(self):
        """Submit shift registration"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approve shift registration and create attendance records"""
        for record in self:
            record.write({'state': 'approved'})
            record._create_attendance_records()

    def action_draft(self):
        """Back to draft"""
        self.write({'state': 'draft'})

    def _create_attendance_records(self):
        """Auto-create attendance records from approved shifts"""
        self.ensure_one()

        for shift in self.shift_ids:
            if shift.shift_type == 'off':
                continue

            # Check if attendance already exists
            existing = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', f"{shift.date} 00:00:00"),
                ('check_in', '<=', f"{shift.date} 23:59:59"),
            ])

            if existing:
                continue  # Don't overwrite

            # Get standard times from config
            config = self.env['ir.config_parameter'].sudo()
            standard_check_in = config.get_param('hr_salary_advanced.standard_check_in_time', '07:30')
            standard_check_out = config.get_param('hr_salary_advanced.standard_check_out_time', '17:30')
            
            # Create attendance based on shift type
            if shift.shift_type == 'morning':
                check_in = datetime.combine(shift.date, datetime.strptime(standard_check_in, '%H:%M').time())
                check_out = datetime.combine(shift.date, datetime.strptime('12:00', '%H:%M').time())
            elif shift.shift_type == 'afternoon':
                check_in = datetime.combine(shift.date, datetime.strptime('13:00', '%H:%M').time())
                check_out = datetime.combine(shift.date, datetime.strptime(standard_check_out, '%H:%M').time())
            elif shift.shift_type == 'full':
                check_in = datetime.combine(shift.date, datetime.strptime(standard_check_in, '%H:%M').time())
                check_out = datetime.combine(shift.date, datetime.strptime(standard_check_out, '%H:%M').time())
            else:
                continue

            self.env['hr.attendance'].create({
                'employee_id': self.employee_id.id,
                'check_in': check_in,
                'check_out': check_out,
            })


class HrShiftDetail(models.Model):
    """Model for individual shift details"""
    _name = 'hr.shift.detail'
    _description = 'Chi Tiết Ca Làm'
    _order = 'date'

    register_id = fields.Many2one(
        'hr.shift.register',
        string='Đăng Ký Ca',
        required=True,
        ondelete='cascade'
    )

    date = fields.Date(
        string='Ngày',
        required=True
    )

    shift_type = fields.Selection(
        [
            ('morning', 'Sáng (08:30-12:00)'),
            ('afternoon', 'Chiều (13:00-17:30)'),
            ('full', 'Cả Ngày (08:30-17:30)'),
            ('off', 'Nghỉ'),
        ],
        string='Loại Ca',
        default='full'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        related='register_id.employee_id',
        store=True
    )

    month = fields.Char(
        string='Tháng',
        related='register_id.month',
        store=True
    )
