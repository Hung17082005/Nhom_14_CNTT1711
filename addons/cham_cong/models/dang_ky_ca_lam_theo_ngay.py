from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DangKyCaLamTheoNgay(models.Model):
    _name = 'dang_ky_ca_lam_theo_ngay'
    _description = "Đăng ký ca làm theo ngày"
    _rec_name = 'ma_dot_ngay'

    _order = 'dot_dang_ky_id desc, ngay_lam asc'

    ma_dot_ngay = fields.Char("Mã đợt ngày", required=True)
    dot_dang_ky_id = fields.Many2one(
        'dot_dang_ky', 
        string="Đợt đăng ký", 
        required=True, 
        ondelete='cascade'
    )
    
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    ngay_lam = fields.Date(string="Ngày làm", required=True)
    
    ca_lam = fields.Selection([
        ("", ""),
        ("Sáng", "Sáng"),
        ("Chiều", "Chiều"),
        ("Cả ngày", "Cả Ngày"),
    ], string="Ca làm", default="")

    @api.constrains('ngay_lam', 'dot_dang_ky_id')
    def _check_ngay_lam(self):
        for record in self:
            dot = record.dot_dang_ky_id
            if record.ngay_lam and dot:
                if record.ngay_lam < dot.ngay_bat_dau or record.ngay_lam > dot.ngay_ket_thuc:
                    raise ValidationError(
                        f'Lỗi: Ngày làm ({record.ngay_lam}) phải nằm trong khoảng thời gian của '
                        f'đợt đăng ký (từ {dot.ngay_bat_dau} đến {dot.ngay_ket_thuc})'
                    )

    @api.constrains('nhan_vien_id', 'dot_dang_ky_id')
    def _check_nhan_vien_in_dot_dang_ky(self):
        for record in self:
            if record.nhan_vien_id and record.dot_dang_ky_id:
                if record.nhan_vien_id.id not in record.dot_dang_ky_id.nhan_vien_ids.ids:
                    raise ValidationError(
                        f'Lỗi: Nhân viên {record.nhan_vien_id.ho_va_ten} không có tên trong '
                        f'danh sách được phép đăng ký của đợt này!'
                    )