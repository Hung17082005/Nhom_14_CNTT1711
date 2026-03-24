from odoo import models, fields
from datetime import datetime


class HrShiftDetail(models.Model):
    """Shift detail for each day"""
    _name = 'hr.shift.detail'
    _description = 'Chi Tiết Ca Làm Việc'
    _order = 'date, id'

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
            ('morning', 'Ca Sáng (7:30-12:00)'),
            ('afternoon', 'Ca Chiều (13:00-17:30)'),
            ('full', 'Ca Đủ (7:30-17:30)'),
            ('off', 'Nghỉ'),
        ],
        string='Loại Ca',
        required=True,
        default='full'
    )

    note = fields.Text(string='Ghi Chú')
