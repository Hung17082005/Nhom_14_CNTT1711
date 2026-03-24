from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BangLuong(models.Model):
    """
    Model phiếu lương tháng của nhân viên.
    Tương ứng với hr.payslip nhưng với logic tính phạt đi muộn tự động.
    """
    _name = 'bang.luong'
    _description = 'Phiếu lương (Bảng lương)'
    _order = 'month desc, employee_id'

    # Nhân viên
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        required=True,
        ondelete='cascade'
    )

    # Tháng tính lương (format: YYYY-MM, ví dụ 2024-01)
    month = fields.Char(
        string='Tháng',
        required=True,
        help='Định dạng YYYY-MM (ví dụ: 2024-01)'
    )

    # Các dòng chi tiết lương
    line_ids = fields.One2many(
        'bang.luong.line',
        'bang_luong_id',
        string='Chi tiết lương',
        copy=True
    )

    # Tính lương thực nhận (Lương cứng + Thưởng - Phạt)
    thuc_lanh = fields.Float(
        string='Thực lãnh',
        compute='_compute_thuc_lanh',
        store=True,
        help='Lương thực lãnh = Tổng cộng - Tổng trừ'
    )

    # Tổng tiền cộng (Lương + Thưởng + ...)
    tong_cong = fields.Float(
        string='Tổng cộng',
        compute='_compute_tong_cong',
        store=True
    )

    # Tổng tiền trừ (Phạt + ...)
    tong_tru = fields.Float(
        string='Tổng trừ',
        compute='_compute_tong_tru',
        store=True
    )

    # Trạng thái
    state = fields.Selection(
        [('draft', 'Bản nháp'), ('done', 'Hoàn tất'), ('cancel', 'Hủy')],
        string='Trạng thái',
        default='draft',
        track_visibility='onchange'
    )

    # Ghi chú
    notes = fields.Text(string='Ghi chú')

    # Ngày tạo/cập nhật
    created_date = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now
    )
    
    # ✅ FIELDS MỚI ĐỂ THEO DÕI CÁC KHOẢN
    # Tổng phút đi muộn trong tháng
    total_late_minutes = fields.Integer(
        string='Tổng phút đi muộn',
        compute='_compute_total_late_minutes',
        store=True,
        help='Tổng số phút đi muộn trong tháng này'
    )
    
    # Tổng tiền phạt đi muộn
    total_late_penalty = fields.Float(
        string='Tổng phạt đi muộn',
        compute='_compute_total_late_penalty',
        store=True,
        help='Tổng số tiền phạt đi muộn'
    )
    
    # Tổng tiền bảo hiểm
    total_insurance = fields.Float(
        string='Tổng bảo hiểm',
        compute='_compute_total_insurance',
        store=True,
        help='Tổng bảo hiểm BHXH + BHYT + BHTN'
    )
    
    # Tổng giờ làm việc trong tháng
    total_work_hours = fields.Float(
        string='Tổng giờ làm việc',
        compute='_compute_total_work_hours',
        store=True,
        help='Tổng số giờ làm việc thực tế trong tháng'
    )

    @api.depends('line_ids.amount', 'line_ids.type')
    def _compute_thuc_lanh(self):
        """
        Tính lương thực nhận.
        Công thức: thực_lãnh = Tổng_cộng - Tổng_trừ
        """
        for record in self:
            record.thuc_lanh = record.tong_cong - record.tong_tru

    @api.depends('line_ids.amount', 'line_ids.type')
    def _compute_tong_cong(self):
        """Tính tổng tiền cộng"""
        for record in self:
            record.tong_cong = sum(
                line.amount for line in record.line_ids 
                if line.type == 'cong'
            )

    @api.depends('line_ids.amount', 'line_ids.type')
    def _compute_tong_tru(self):
        """Tính tổng tiền trừ"""
        for record in self:
            record.tong_tru = sum(
                line.amount for line in record.line_ids 
                if line.type == 'tru'
            )

    def action_generate_lines(self):
        """
        Tự động sinh các dòng lương dựa trên:
        - Lương cơ bản từ hợp đồng
        - Phạt đi muộn/về sớm trong tháng
        - Bảo hiểm (BHXH, BHYT, BHTN)
        - Các thưởng (nếu có cấu hình)
        """
        for record in self:
            # Xóa các dòng cũ (nếu có)
            record.line_ids.unlink()

            # Tạo danh sách dòng lương
            lines_to_create = []

            # 1. Lương cơ bản
            line_luong_co_ban = record._get_luong_co_ban()
            if line_luong_co_ban:
                lines_to_create.append(line_luong_co_ban)

            # 2. Phạt đi muộn
            lines_phat = record._calculate_phat_lines()
            lines_to_create.extend(lines_phat)

            # 3. ✅ NEW: Bảo hiểm
            lines_insurance = record._calculate_insurance_lines()
            lines_to_create.extend(lines_insurance)

            # 4. Các khoản thưởng (nếu có cấu hình riêng)
            # Bạn có thể mở rộng logic này

            # Tạo tất cả dòng cùng lúc
            for line_data in lines_to_create:
                self.env['bang.luong.line'].create(line_data)

    def _get_luong_co_ban(self):
        """
        Tính lương cơ bản theo công thức: Lương cơ bản / 26 ngày × Số ngày làm thực tế
        
        Ví dụ: 10 triệu / 26 ngày = 384,615 VND/ngày
        Nếu làm 20 ngày = 384,615 × 20 = 7,692,307 VND
        """
        self.ensure_one()
        
        if not self.employee_id or not self.month:
            return None

        # Lấy lương hợp đồng
        monthly_wage = 0.0
        contract = self.employee_id.contract_id
        
        if contract and contract.wage:
            monthly_wage = contract.wage
        else:
            # Lấy từ config
            default_wage = self.env['ir.config_parameter'].sudo().get_param(
                'hr_salary_custom.default_wage', '0'
            )
            try:
                monthly_wage = float(default_wage)
            except (ValueError, TypeError):
                monthly_wage = 0.0

        if monthly_wage <= 0:
            return None

        # Tính số ngày làm thực tế trong tháng
        try:
            year, month_num = map(int, self.month.split('-'))
            start_date = datetime(year, month_num, 1).date()
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month_num + 1, 1).date() - timedelta(days=1)
        except (ValueError, IndexError):
            return None

        # Lấy attendance records trong tháng (chỉ tính những ngày có check_in)
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', f'{start_date} 00:00:00'),
            ('check_in', '<=', f'{end_date} 23:59:59'),
        ])

        # Đếm số ngày làm việc (distinct dates)
        working_dates = set()
        for att in attendances:
            check_in_date = att.check_in.date() if att.check_in else None
            if check_in_date:
                working_dates.add(check_in_date)
        
        actual_working_days = len(working_dates)
        
        if actual_working_days <= 0:
            # Nếu chưa có attendance, không tính lương
            return None

        # Tính lương theo ngày
        # Công thức: Lương = (Lương hợp đồng / 26) × Số ngày làm
        daily_rate = monthly_wage / 26.0
        total_wage = daily_rate * actual_working_days

        return {
            'bang_luong_id': self.id,
            'name': f'Lương cơ bản ({actual_working_days} ngày × {daily_rate:,.2f})',
            'amount': total_wage,
            'type': 'cong',
            'sequence': 10,
            'description': (
                f'Tính lương: {monthly_wage:,.0f} / 26 ngày = {daily_rate:,.2f} VND/ngày × {actual_working_days} ngày = {total_wage:,.2f}'
            )
        }

    def _calculate_phat_lines(self):
        """
        Tính lương phạt dựa trên:
        - Tổng số phút đi muộn trong tháng
        - Phạt theo cấu hình: VND/phút
        """
        self.ensure_one()
        lines = []

        if not self.employee_id or not self.month:
            return lines

        # Phân tích tháng (format: YYYY-MM)
        try:
            year, month = map(int, self.month.split('-'))
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        except (ValueError, IndexError):
            return lines

        # Lấy tất cả attendance records trong tháng
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', f'{start_date} 00:00:00'),
            ('check_in', '<=', f'{end_date} 23:59:59'),
        ])

        # Tính tổng phút muộn
        total_late_minutes = sum(att.late_minutes for att in attendances if att.is_late)

        if total_late_minutes > 0:
            # Lấy mức phạt từ config (VND/phút, mặc định 1000)
            penalty_per_minute = self.env['ir.config_parameter'].sudo().get_param(
                'hr_salary_custom.penalty_per_minute',
                '1000'
            )
            
            try:
                penalty_per_minute = float(penalty_per_minute)
            except (ValueError, TypeError):
                penalty_per_minute = 1000.0

            phat_tien = total_late_minutes * penalty_per_minute

            lines.append({
                'bang_luong_id': self.id,
                'name': 'Phạt đi muộn',
                'amount': phat_tien,
                'type': 'tru',
                'sequence': 50,
                'description': f'Phạt {total_late_minutes} phút đi muộn @ {penalty_per_minute:,.0f} VND/phút'
            })

        return lines

    def action_confirm(self):
        """Xác nhận phiếu lương"""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Hủy phiếu lương"""
        self.write({'state': 'cancel'})

    def action_draft(self):
        """Quay lại bản nháp"""
        self.write({'state': 'draft'})

    @api.model
    def create_payslips_for_month(self, employee_id, month):
        """
        Tạo phiếu lương cho nhân viên trong tháng cụ thể.
        Tự động sinh các dòng lương.
        
        Args:
            employee_id: ID của nhân viên
            month: Tháng (format: YYYY-MM)
        """
        # Kiểm tra xem đã tồn tại chưa
        existing = self.search([
            ('employee_id', '=', employee_id),
            ('month', '=', month)
        ])
        
        if existing:
            return existing[0]

        # Tạo phiếu lương mới
        payslip = self.create({
            'employee_id': employee_id,
            'month': month
        })

        # Tự động sinh dòng lương
        payslip.action_generate_lines()

        return payslip

    def _calculate_insurance_lines(self):
        """
        ✅ NEW: Tính bảo hiểm (BHXH, BHYT, BHTN)
        Bảo hiểm được tính dựa trên LƯƠNG THỰC THU (sau khi tính theo ngày làm việc)
        
        Công thức:
        - BHXH: 8% 
        - BHYT: 1.5% 
        - BHTN: 1% 
        - Tổng bảo hiểm = (BHXH + BHYT + BHTN) × Lương thực
        
        Các tỷ lệ lấy từ config (có thể cấu hình)
        """
        self.ensure_one()
        lines = []

        if not self.employee_id or not self.month:
            return lines

        # Lấy lương thực (theo số ngày làm), không lấy lương hợp đồng toàn bộ
        luong_thuc = 0.0
        
        try:
            year, month_num = map(int, self.month.split('-'))
            start_date = datetime(year, month_num, 1).date()
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month_num + 1, 1).date() - timedelta(days=1)
        except (ValueError, IndexError):
            return lines

        # Lấy attendance records và tính số ngày làm
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', f'{start_date} 00:00:00'),
            ('check_in', '<=', f'{end_date} 23:59:59'),
        ])

        working_dates = set()
        for att in attendances:
            check_in_date = att.check_in.date() if att.check_in else None
            if check_in_date:
                working_dates.add(check_in_date)
        
        actual_working_days = len(working_dates)
        
        if actual_working_days <= 0:
            return lines

        # Lấy lương hợp đồng để tính lương thực
        contract = self.employee_id.contract_id
        if contract and contract.wage:
            monthly_wage = contract.wage
        else:
            default_wage = self.env['ir.config_parameter'].sudo().get_param(
                'hr_salary_custom.default_wage', '0'
            )
            try:
                monthly_wage = float(default_wage)
            except (ValueError, TypeError):
                monthly_wage = 0.0

        if monthly_wage <= 0:
            return lines

        # Lương thực = (lương hợp đồng / 26) × số ngày làm
        daily_rate = monthly_wage / 26.0
        luong_thuc = daily_rate * actual_working_days

        # Lấy tỷ lệ bảo hiểm từ config
        rate_bhxh = float(self.env['ir.config_parameter'].sudo().get_param(
            'hr_salary_custom.insurance_bhxh_rate', '0.08'  # 8%
        ))
        rate_bhyt = float(self.env['ir.config_parameter'].sudo().get_param(
            'hr_salary_custom.insurance_bhyt_rate', '0.015'  # 1.5%
        ))
        rate_bhtn = float(self.env['ir.config_parameter'].sudo().get_param(
            'hr_salary_custom.insurance_bhtn_rate', '0.01'   # 1%
        ))

        # Tính bảo hiểm từng loại (dựa trên lương thực)
        bhxh = luong_thuc * rate_bhxh
        bhyt = luong_thuc * rate_bhyt
        bhtn = luong_thuc * rate_bhtn
        total_insurance = bhxh + bhyt + bhtn

        if total_insurance > 0:
            lines.append({
                'bang_luong_id': self.id,
                'name': 'Bảo hiểm (BHXH, BHYT, BHTN)',
                'amount': total_insurance,
                'type': 'tru',
                'sequence': 60,
                'description': (
                    f'BHXH ({rate_bhxh*100}%): {bhxh:,.0f} + '
                    f'BHYT ({rate_bhyt*100}%): {bhyt:,.0f} + '
                    f'BHTN ({rate_bhtn*100}%): {bhtn:,.0f} = {total_insurance:,.0f}'
                )
            })

        return lines

    # ✅ COMPUTED FIELDS CHO TÍNH NĂNG THEO DÕI

    @api.depends('line_ids.late_minutes')
    def _compute_total_late_minutes(self):
        """Tính tổng phút đi muộn từ dòng lương"""
        # Lấy từ attendance records thực tế
        for record in self:
            if not record.employee_id or not record.month:
                record.total_late_minutes = 0
                continue

            try:
                year, month = map(int, record.month.split('-'))
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            except (ValueError, IndexError):
                record.total_late_minutes = 0
                continue

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', f'{start_date} 00:00:00'),
                ('check_in', '<=', f'{end_date} 23:59:59'),
                ('is_late', '=', True)
            ])

            record.total_late_minutes = sum(
                att.late_minutes for att in attendances
            )

    @api.depends('line_ids.amount', 'line_ids.name')
    def _compute_total_late_penalty(self):
        """Tính tổng phạt đi muộn từ dòng lương"""
        for record in self:
            total = 0.0
            for line in record.line_ids:
                if 'muộn' in (line.name or '').lower() and line.type == 'tru':
                    total += line.amount
            record.total_late_penalty = total

    @api.depends('line_ids.amount', 'line_ids.name')
    def _compute_total_insurance(self):
        """Tính tổng bảo hiểm từ dòng lương"""
        for record in self:
            total = 0.0
            for line in record.line_ids:
                if 'bảo hiểm' in (line.name or '').lower() and line.type == 'tru':
                    total += line.amount
            record.total_insurance = total

    @api.depends('line_ids.worked_hours')
    def _compute_total_work_hours(self):
        """Tính tổng giờ làm việc từ attendance records"""
        for record in self:
            if not record.employee_id or not record.month:
                record.total_work_hours = 0.0
                continue

            try:
                year, month = map(int, record.month.split('-'))
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            except (ValueError, IndexError):
                record.total_work_hours = 0.0
                continue

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', f'{start_date} 00:00:00'),
                ('check_in', '<=', f'{end_date} 23:59:59'),
            ])

            # Tính tổng giờ từ field work_hours_computed
            record.total_work_hours = sum(
                att.work_hours_computed for att in attendances
            )
