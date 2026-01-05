from odoo import models, fields, api
from datetime import datetime
import calendar

class PhieuLuong(models.Model):
    _name = 'hr_phieu_luong'
    _description = 'Phiếu lương nhân viên'
    _inherit = ['mail.thread']

    name = fields.Char(string="Số phiếu", compute="_compute_name", store=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    
    thang = fields.Selection([
        ('1', 'T1'), ('2', 'T2'), ('3', 'T3'), ('4', 'T4'), ('5', 'T5'), ('6', 'T6'),
        ('7', 'T7'), ('8', 'T8'), ('9', 'T9'), ('10', 'T10'), ('11', 'T11'), ('12', 'T12')
    ], string="Tháng", required=True, default=lambda self: str(datetime.now().month))
    nam = fields.Integer(string="Năm", default=lambda self: datetime.now().year)

    # Lấy lương cơ bản từ hồ sơ nhân viên (giả định field là luong_co_ban)
    luong_co_ban = fields.Float(related="nhan_vien_id.luong_co_ban", string="Lương cơ bản", store=True)
    
    # Dữ liệu quét tự động từ module cham_cong
    tong_gio_lam = fields.Float(string="Tổng giờ làm", compute="_compute_du_lieu_cham_cong")
    phut_muon = fields.Float(string="Phút đi muộn", compute="_compute_du_lieu_cham_cong")
    
    tien_phat = fields.Float(string="Tiền phạt muộn", compute="_compute_thanh_tien")
    thuc_linh = fields.Float(string="Thực lĩnh", compute="_compute_thanh_tien", store=True, tracking=True)

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_name(self):
        for rec in self:
            rec.name = f"PL/{rec.nhan_vien_id.ho_va_ten}/{rec.thang}-{rec.nam}"

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_du_lieu_cham_cong(self):
        for rec in self:
            if rec.nhan_vien_id and rec.thang and rec.nam:
                # Xác định ngày đầu và cuối tháng
                ngay_dau = datetime(rec.nam, int(rec.thang), 1).date()
                ngay_cuoi = datetime(rec.nam, int(rec.thang), calendar.monthrange(rec.nam, int(rec.thang))[1]).date()
                
                # Tìm dữ liệu bên module cham_cong
                records = self.env['bang_cham_cong'].search([
                    ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                    ('ngay_cham_cong', '>=', ngay_dau),
                    ('ngay_cham_cong', '<=', ngay_cuoi)
                ])
                rec.tong_gio_lam = sum(records.mapped('tong_gio_lam'))
                rec.phut_muon = sum(records.mapped('phut_di_muon'))
            else:
                rec.tong_gio_lam = rec.phut_muon = 0

    @api.depends('tong_gio_lam', 'phut_muon', 'luong_co_ban')
    def _compute_thanh_tien(self):
        for rec in self:
            # 208h là giờ chuẩn 1 tháng (26 ngày * 8 tiếng)
            don_gia_gio = rec.luong_co_ban / 208
            rec.tien_phat = rec.phut_muon * 2000 # Ví dụ phạt 2k/phút
            rec.thuc_linh = (rec.tong_gio_lam * don_gia_gio) - rec.tien_phat