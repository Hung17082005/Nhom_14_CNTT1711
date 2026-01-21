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

    # Lấy lương cơ bản từ hồ sơ nhân viên 
    luong_co_ban = fields.Float(related="nhan_vien_id.luong_co_ban", string="Lương cơ bản", store=True)
    
    # Dữ liệu quét tự động từ module cham_cong
    tong_gio_lam = fields.Float(string="Tổng giờ làm", compute="_compute_du_lieu_cham_cong")
    phut_muon = fields.Float(string="Phút đi muộn", compute="_compute_du_lieu_cham_cong")
    
    tien_phat = fields.Float(string="Tiền phạt muộn", compute="_compute_thanh_tien")
    thuc_linh = fields.Float(string="Thực lĩnh", compute="_compute_thanh_tien", store=True, tracking=True)
    
    bhxh = fields.Float(string="BHXH (8%)", compute="_compute_thanh_tien")
    bhyt = fields.Float(string="BHYT (1.5%)", compute="_compute_thanh_tien")
    bhtn = fields.Float(string="BHTN (1%)", compute="_compute_thanh_tien")
    tong_bao_hiem = fields.Float(string="Tổng bảo hiểm", compute="_compute_thanh_tien")
    cp_bh_cong_ty = fields.Float(string="Công ty đóng thêm (21.5%)", compute="_compute_thanh_tien")

    cp_bh_xh_cty = fields.Float(string="Cty đóng BHXH", compute="_compute_thanh_tien")
    cp_bh_yt_cty = fields.Float(string="Cty đóng BHYT", compute="_compute_thanh_tien")
    cp_bh_tn_cty = fields.Float(string="Cty đóng BHTN", compute="_compute_thanh_tien")
    tong_cp_bh_cty = fields.Float(string="Tổng Cty hỗ trợ", compute="_compute_thanh_tien")
    tinh_trang_ho_tro = fields.Char(string="Chế độ bảo hiểm", compute="_compute_thanh_tien")
    
    #phụ cấp
    luong_thuc_te_hien_thi = fields.Float(string="Lương thực nhận", compute="_compute_thanh_tien")
    phu_cap_nhan_su = fields.Float(related="nhan_vien_id.phu_cap", string="Phụ cấp gốc", store=True)
    phu_cap_thuc_te = fields.Float(string="Phụ cấp theo giờ", compute="_compute_thanh_tien")
    tinh_trang_ho_tro = fields.Char(string="Chế độ bảo hiểm", compute="_compute_thanh_tien")

    line_ids = fields.One2many(
        'bang_cham_cong', 
        compute="_compute_du_lieu_cham_cong", # Dùng chung hàm với dữ liệu tổng để tối ưu
        string="Chi tiết chấm công"
    )

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

    @api.depends('tong_gio_lam', 'luong_co_ban', 'phu_cap_nhan_su', 'phut_muon')
    def _compute_thanh_tien(self):
        for rec in self:
        
            rec.luong_thuc_te_hien_thi = 0.0
            rec.phu_cap_thuc_te = 0.0
            rec.tien_phat = 0.0
            rec.thuc_linh = 0.0
            rec.bhxh = 0.0  
            rec.bhyt = 0.0
            rec.bhtn = 0.0
            rec.tong_bao_hiem = 0.0
            rec.tinh_trang_ho_tro = "Công ty hỗ trợ 100%"

            # Tính toán tỷ lệ công
            # 208 là giờ công chuẩn
            ty_le_cong = rec.tong_gio_lam / 208 if rec.tong_gio_lam > 0 else 0
            
            if rec.luong_co_ban > 0:
                # Gán giá trị tính toán
                rec.luong_thuc_te_hien_thi = rec.luong_co_ban * ty_le_cong
                rec.phu_cap_thuc_te = rec.phu_cap_nhan_su * ty_le_cong
                
                # Tính bảo hiểm 
                rec.bhxh = rec.luong_thuc_te_hien_thi * 0.08
                rec.bhyt = rec.luong_thuc_te_hien_thi * 0.015
                rec.bhtn = rec.luong_thuc_te_hien_thi * 0.01
                rec.tong_bao_hiem = rec.bhxh + rec.bhyt + rec.bhtn
                
                # Tính thực lĩnh
                rec.tien_phat = rec.phut_muon * 2000
                rec.thuc_linh = rec.luong_thuc_te_hien_thi + rec.phu_cap_thuc_te - rec.tien_phat

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_du_lieu_cham_cong(self):
        for rec in self:
            rec.line_ids = self.env['bang_cham_cong'] 
            
            if rec.nhan_vien_id and rec.thang and rec.nam:
                try:
                    # Xác định ngày đầu và cuối tháng
                    ngay_dau = datetime(rec.nam, int(rec.thang), 1).date()
                    ngay_cuoi = datetime(rec.nam, int(rec.thang), calendar.monthrange(rec.nam, int(rec.thang))[1]).date()
                    
                    # Tìm dữ liệu bên module cham_cong
                    records = self.env['bang_cham_cong'].search([
                        ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                        ('ngay_cham_cong', '>=', ngay_dau),
                        ('ngay_cham_cong', '<=', ngay_cuoi)
                    ])
                    
                    # Gán danh sách các dòng chấm công tìm được
                    rec.line_ids = records
                    
                    # Tính toán số liệu tổng
                    rec.tong_gio_lam = sum(records.mapped('tong_gio_lam'))
                    rec.phut_muon = sum(records.mapped('phut_di_muon'))
                except Exception:
                    rec.tong_gio_lam = 0
                    rec.phut_muon = 0
            else:
                rec.tong_gio_lam = 0
                rec.phut_muon = 0