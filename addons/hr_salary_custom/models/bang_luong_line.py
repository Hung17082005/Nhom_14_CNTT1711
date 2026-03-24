from odoo import models, fields, api


class BangLuongLine(models.Model):
    """
    Model lưu các dòng chi tiết trong phiếu lương.
    Bao gồm: Lương cơ bản, Thưởng, Phạt, v.v.
    """
    _name = 'bang.luong.line'
    _description = 'Chi tiết phiếu lương'
    _order = 'sequence,id'

    # Link với model cha
    bang_luong_id = fields.Many2one(
        'bang.luong',
        string='Phiếu lương',
        ondelete='cascade',
        required=True
    )

    # Nội dung dòng lương
    name = fields.Char(
        string='Nội dung',
        required=True,
        help='Ví dụ: Lương cứng, Thưởng, Phạt đi muộn, v.v.'
    )

    # Số tiền
    amount = fields.Float(
        string='Số tiền',
        required=True,
        default=0.0,
        help='Nhập số tiền (dương hoặc âm tùy theo loại)'
    )

    # Loại: cộng hay trừ
    type = fields.Selection(
        [('cong', 'Cộng'), ('tru', 'Trừ')],
        string='Loại',
        required=True,
        default='cong',
        help='Cộng = tăng lương, Trừ = giảm lương'
    )

    # Thứ tự sắp xếp
    sequence = fields.Integer(
        string='Thứ tự',
        default=10
    )

    # Mô tả/ghi chú
    description = fields.Text(
        string='Ghi chú',
        help='Mô tả chi tiết về khoản lương này'
    )
