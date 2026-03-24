from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Attendance
    standard_check_in_time = fields.Char(
        string='Giờ Chuẩn Check-in',
        config_parameter='hr_salary_advanced.standard_check_in_time',
        default='07:30',
        help='Format: HH:MM (e.g., 07:30)'
    )

    standard_check_out_time = fields.Char(
        string='Giờ Chuẩn Check-out',
        config_parameter='hr_salary_advanced.standard_check_out_time',
        default='17:30',
        help='Format: HH:MM (e.g., 17:30)'
    )

    # Salary calculation
    basic_salary = fields.Float(
        string='Lương Cơ Bản',
        config_parameter='hr_salary_advanced.basic_salary',
        default=10000000.0,
        help='Default monthly base salary'
    )

    standard_working_days = fields.Integer(
        string='Số Công Chuẩn',
        config_parameter='hr_salary_advanced.standard_working_days',
        default=26,
        help='Standard working days per month'
    )

    overtime_rate = fields.Float(
        string='Thưởng Công Vượt (VND/ngày)',
        config_parameter='hr_salary_advanced.overtime_rate',
        default=500000.0,
        help='Bonus per overtime day'
    )

    # Late penalty
    penalty_per_minute = fields.Float(
        string='Phạt/Phút Muộn',
        config_parameter='hr_salary_advanced.penalty_per_minute',
        default=10000.0,
        help='Late penalty per minute (VND)'
    )

    # Insurance rates
    insurance_bhxh_rate = fields.Float(
        string='Tỷ Lệ BHXH (%)',
        config_parameter='hr_salary_advanced.insurance_bhxh_rate',
        default=0.08,
        help='BHXH rate (Social Insurance)'
    )

    insurance_bhyt_rate = fields.Float(
        string='Tỷ Lệ BHYT (%)',
        config_parameter='hr_salary_advanced.insurance_bhyt_rate',
        default=0.015,
        help='BHYT rate (Health Insurance)'
    )

    insurance_bhtn_rate = fields.Float(
        string='Tỷ Lệ BHTN (%)',
        config_parameter='hr_salary_advanced.insurance_bhtn_rate',
        default=0.01,
        help='BHTN rate (Unemployment Insurance)'
    )
