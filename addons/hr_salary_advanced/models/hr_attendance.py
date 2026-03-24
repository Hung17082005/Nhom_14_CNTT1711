from odoo import models, fields, api
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    """Extend hr.attendance with late detection"""
    _inherit = 'hr.attendance'

    # Add fields for late tracking
    is_late = fields.Boolean(
        string='Đi Muộn',
        compute='_compute_is_late',
        store=True,
        help='Tự động đánh dấu nếu check-in sau 07:30'
    )

    late_minutes = fields.Integer(
        string='Phút Muộn',
        compute='_compute_late_minutes',
        store=True,
        help='Số phút trễ so với giờ chuẩn'
    )

    @api.depends('check_in')
    def _compute_is_late(self):
        """Check if check-in is after standard time (07:30)"""
        config = self.env['ir.config_parameter'].sudo()
        standard_time_str = config.get_param('hr_salary_advanced.standard_check_in_time', '07:30')

        for record in self:
            if not record.check_in:
                record.is_late = False
                continue

            try:
                # Parse standard time (HH:MM)
                hour, minute = map(int, standard_time_str.split(':'))
                check_in_time = record.check_in.time()
                standard_time = datetime.strptime(standard_time_str, '%H:%M').time()

                record.is_late = check_in_time > standard_time
            except (ValueError, AttributeError):
                record.is_late = False

    @api.depends('check_in')
    def _compute_late_minutes(self):
        """Calculate minutes late"""
        config = self.env['ir.config_parameter'].sudo()
        standard_time_str = config.get_param('hr_salary_advanced.standard_check_in_time', '07:30')

        for record in self:
            if not record.check_in or not record.is_late:
                record.late_minutes = 0
                continue

            try:
                standard_time = datetime.strptime(standard_time_str, '%H:%M').time()
                check_in_time = record.check_in.time()

                # Convert to minutes for comparison
                standard_minutes = standard_time.hour * 60 + standard_time.minute
                check_in_minutes = check_in_time.hour * 60 + check_in_time.minute

                record.late_minutes = max(0, check_in_minutes - standard_minutes)
            except (ValueError, AttributeError):
                record.late_minutes = 0
