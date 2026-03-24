from odoo import models, fields


class BangLuongLine(models.Model):
    """Payslip detail line"""
    _name = 'bang.luong.line'
    _description = 'Chi Tiết Dòng Lương'
    _order = 'sequence, id'

    bang_luong_id = fields.Many2one(
        'bang.luong',
        string='Phiếu Lương',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(string='Thứ Tự', default=10)

    name = fields.Char(
        string='Nội Dung',
        required=True
    )

    amount = fields.Float(
        string='Số Tiền',
        required=True,
        default=0.0
    )

    type = fields.Selection(
        [('cong', 'Cộng (+)'), ('tru', 'Trừ (-)')],
        string='Loại',
        required=True,
        default='cong'
    )

    description = fields.Text(
        string='Ghi Chú',
        help='Chi tiết hoặc công thức tính'
    )
