from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    luong_co_ban = fields.Float("Lương cơ bản")
    phu_cap_chuc_vu = fields.Float("Phụ cấp chức vụ")
    
    # Dùng để hiển thị ký hiệu VNĐ
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', 
                                  default=lambda self: self.env.ref('base.VND').id)