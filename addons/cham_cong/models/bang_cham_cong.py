from odoo import models, fields, api
from datetime import datetime, time
from odoo.exceptions import ValidationError
from pytz import timezone, UTC

class BangChamCong(models.Model):
    _name = 'bang_cham_cong'
    _description = "Bảng chấm công"
    _rec_name = 'Id_BCC'
    _order = 'ngay_cham_cong desc, nhan_vien_id'

    # --- Các trường cơ bản ---
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    ngay_cham_cong = fields.Date("Ngày chấm công", required=True, default=fields.Date.context_today)
    Id_BCC = fields.Char(string="ID BCC", compute="_compute_Id_BCC", store=True)

    @api.depends('nhan_vien_id', 'ngay_cham_cong')
    def _compute_Id_BCC(self):
        for record in self:
            if record.nhan_vien_id and record.ngay_cham_cong:
                record.Id_BCC = f"{record.nhan_vien_id.ho_va_ten}_{record.ngay_cham_cong}"
            else:
                record.Id_BCC = "Mới"

    # --- Liên kết ca làm và Đơn từ ---
    dang_ky_ca_lam_id = fields.Many2one('dang_ky_ca_lam_theo_ngay', string="Đăng ký ca làm")
    ca_lam = fields.Selection(related='dang_ky_ca_lam_id.ca_lam', store=True, string="Ca làm")
    
    don_tu_id = fields.Many2one('don_tu', string="Đơn từ liên quan")
    loai_don = fields.Selection(related='don_tu_id.loai_don', string="Loại đơn", store=True)
    thoi_gian_xin = fields.Float(related='don_tu_id.thoi_gian_xin', string="Thời gian xin (phút)", store=True)
    trang_thai_duyet_don = fields.Selection(related='don_tu_id.trang_thai_duyet', string="Trạng thái duyệt đơn", store=True)

    # --- Logic Tự động tìm Ca làm và Đơn từ ---
    @api.onchange('nhan_vien_id', 'ngay_cham_cong')
    def _onchange_data_lien_quan(self):
        for record in self:
            if record.nhan_vien_id and record.ngay_cham_cong:
                # 1. Tìm ca làm
                dk_ca = self.env['dang_ky_ca_lam_theo_ngay'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_lam', '=', record.ngay_cham_cong)
                ], limit=1)
                record.dang_ky_ca_lam_id = dk_ca.id if dk_ca else False

                # 2. Tìm đơn từ (Chỉ lấy đơn đã duyệt)
                don = self.env['don_tu'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_ap_dung', '=', record.ngay_cham_cong),
                    ('trang_thai_duyet', '=', 'da_duyet')
                ], limit=1)
                record.don_tu_id = don.id if don else False

    # --- Thời gian quy định (Xử lý múi giờ) ---
    gio_vao_ca = fields.Datetime("Giờ vào ca quy định", compute='_compute_gio_ca', store=True)
    gio_ra_ca = fields.Datetime("Giờ ra ca quy định", compute='_compute_gio_ca', store=True)
    
    @api.depends('ca_lam', 'ngay_cham_cong')
    def _compute_gio_ca(self):
        user_tz = self.env.user.tz or 'Asia/Ho_Chi_Minh'
        tz = timezone(user_tz)
        for record in self:
            if not record.ngay_cham_cong or not record.ca_lam:
                record.gio_vao_ca = record.gio_ra_ca = False
                continue

            if record.ca_lam == "Sáng":
                v, r = time(7, 30), time(11, 30)
            elif record.ca_lam == "Chiều":
                v, r = time(13, 30), time(17, 30)
            else: # Cả ngày
                v, r = time(7, 30), time(17, 30)

            dt_vao = tz.localize(datetime.combine(record.ngay_cham_cong, v)).astimezone(UTC).replace(tzinfo=None)
            dt_ra = tz.localize(datetime.combine(record.ngay_cham_cong, r)).astimezone(UTC).replace(tzinfo=None)
            record.gio_vao_ca = dt_vao
            record.gio_ra_ca = dt_ra

    # --- Thời gian thực tế ---
    gio_vao = fields.Datetime("Giờ vào thực tế")
    gio_ra = fields.Datetime("Giờ ra thực tế")
    tong_gio_lam = fields.Float("Tổng giờ làm thực tế", compute="_compute_tong_gio_lam", store=True)

    @api.depends('gio_vao', 'gio_ra', 'ca_lam', 'loai_don', 'trang_thai_duyet_don')
    def _compute_tong_gio_lam(self):
        for record in self:
            tong_gio = 0.0
            # Trường hợp 1: Có đi làm (có quét vân tay)
            if record.gio_vao and record.gio_ra:
                delta = record.gio_ra - record.gio_vao
                tong_gio = delta.total_seconds() / 3600
                if record.ca_lam == 'Cả ngày' and tong_gio > 5:
                    tong_gio -= 1.0 # Trừ giờ nghỉ trưa
            
            # Trường hợp 2: Vắng mặt nhưng có đơn nghỉ hưởng lương ('nghi') đã duyệt
            # Hệ thống tự động bù 8 tiếng (đối với ca cả ngày) hoặc 4 tiếng (ca sáng/chiều)
            if (not record.gio_vao or not record.gio_ra) and record.loai_don == 'nghi' and record.trang_thai_duyet_don == 'da_duyet':
                tong_gio = 8.0 if record.ca_lam == 'Cả ngày' else 4.0
            
            record.tong_gio_lam = max(0, tong_gio)

    # --- Tính toán Muộn/Sớm ---
    phut_di_muon = fields.Float("Số phút đi muộn thực tế", compute="_compute_phat", store=True)
    phut_ve_som = fields.Float("Số phút về sớm thực tế", compute="_compute_phat", store=True)
    
    @api.depends('gio_vao', 'gio_ra', 'gio_vao_ca', 'gio_ra_ca', 'don_tu_id', 'thoi_gian_xin')
    def _compute_phat(self):
        for record in self:
            muon = som = 0.0
            if record.gio_vao and record.gio_vao_ca and record.gio_vao > record.gio_vao_ca:
                muon = (record.gio_vao - record.gio_vao_ca).total_seconds() / 60
                # Nếu có đơn 'di_muon' thì trừ bớt thời gian xin
                if record.loai_don == 'di_muon':
                    muon = max(0, muon - record.thoi_gian_xin)
            
            if record.gio_ra and record.gio_ra_ca and record.gio_ra < record.gio_ra_ca:
                som = (record.gio_ra_ca - record.gio_ra).total_seconds() / 60
                # Nếu có đơn 've_som' thì trừ bớt thời gian xin
                if record.loai_don == 've_som':
                    som = max(0, som - record.thoi_gian_xin)
            
            record.phut_di_muon = muon
            record.phut_ve_som = som

    # --- Trạng thái chấm công ---
    trang_thai = fields.Selection([
        ('di_lam', 'Đi làm'),
        ('di_muon', 'Đi muộn'),
        ('ve_som', 'Về sớm'),
        ('di_muon_ve_som', 'Đi muộn & Về sớm'),
        ('vang_mat_co_phep', 'Vắng mặt có phép'),
        ('vang_mat', 'Vắng mặt không phép'),
    ], string="Trạng thái", compute="_compute_trang_thai", store=True)
    
    @api.depends('phut_di_muon', 'phut_ve_som', 'gio_vao', 'gio_ra', 'loai_don', 'trang_thai_duyet_don')
    def _compute_trang_thai(self):
        for record in self:
            if not record.gio_vao or not record.gio_ra:
                if record.loai_don == 'nghi' and record.trang_thai_duyet_don == 'da_duyet':
                    record.trang_thai = 'vang_mat_co_phep'
                else:
                    record.trang_thai = 'vang_mat'
            elif record.phut_di_muon > 0 and record.phut_ve_som > 0:
                record.trang_thai = 'di_muon_ve_som'
            elif record.phut_di_muon > 0:
                record.trang_thai = 'di_muon'
            elif record.phut_ve_som > 0:
                record.trang_thai = 've_som'
            else:
                record.trang_thai = 'di_lam'

    # --- Ghi đè hàm Create/Write để nạp dữ liệu liên quan ---
    @api.model
    def create(self, vals):
        res = super(BangChamCong, self).create(vals)
        res._onchange_data_lien_quan()
        return res

    def write(self, vals):
        res = super(BangChamCong, self).write(vals)
        if 'nhan_vien_id' in vals or 'ngay_cham_cong' in vals:
            self._onchange_data_lien_quan()
        return res