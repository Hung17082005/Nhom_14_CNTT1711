from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BangLuong(models.Model):
    """Payslip (Phiếu Lương)"""
    _name = 'bang.luong'
    _description = 'Phiếu Lương'
    _order = 'month desc, employee_id'

    # Basic info
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân Viên',
        required=True,
        ondelete='cascade'
    )

    month = fields.Char(
        string='Tháng',
        required=True,
        help='Format: YYYY-MM (e.g., 2024-01)'
    )

    state = fields.Selection(
        [('draft', 'Bản Nháp'), ('done', 'Hoàn Tất'), ('cancel', 'Hủy')],
        string='Trạng Thái',
        default='draft'
    )

    # Salary details - Basic wage structure
    basic_salary = fields.Float(
        string='Lương Cơ Bản (Hợp Đồng)',
        compute='_compute_basic_salary',
        store=True,
        help='Monthly base salary from contract'
    )

    standard_days = fields.Integer(
        string='Số Công Chuẩn',
        default=26,
        help='Standard working days per month'
    )

    actual_days = fields.Integer(
        string='Số Công Thực Tế',
        compute='_compute_actual_days',
        store=True,
        help='Actual working days from attendance/shift register'
    )

    overtime_days = fields.Float(
        string='Ngày Công Vượt',
        compute='_compute_overtime_days',
        store=True,
        help='Days worked beyond standard (actual_days - standard_days)'
    )

    # Salary calculations
    salary_by_days = fields.Float(
        string='Lương Theo Công',
        compute='_compute_salary_by_days',
        store=True,
        help='Salary calculated by actual working days'
    )

    overtime_bonus = fields.Float(
        string='Thưởng Công Vượt',
        compute='_compute_overtime_bonus',
        store=True,
        help='Bonus for overtime: overtime_days × rate'
    )

    total_insurance = fields.Float(
        string='Tổng Bảo Hiểm',
        compute='_compute_total_insurance',
        store=True,
        help='BHXH + BHYT + BHTN'
    )

    late_penalty = fields.Float(
        string='Phạt Đi Muộn',
        compute='_compute_late_penalty',
        store=True,
        help='Total late penalty for the month'
    )

    total_deductions = fields.Float(
        string='Tổng Trừ',
        compute='_compute_total_deductions',
        store=True,
        help='Total insurance + late penalty'
    )

    net_salary = fields.Float(
        string='Lương Thực Nhận',
        compute='_compute_net_salary',
        store=True,
        help='Net salary: salary_by_days + overtime_bonus - total_deductions'
    )

    # Line items
    line_ids = fields.One2many(
        'bang.luong.line',
        'bang_luong_id',
        string='Chi Tiết Lương',
        copy=True
    )

    notes = fields.Text(string='Ghi Chú')

    created_date = fields.Datetime(
        string='Ngày Tạo',
        default=fields.Datetime.now
    )

    # ===== COMPUTE FIELDS =====

    @api.depends('employee_id')
    def _compute_basic_salary(self):
        """Get basic salary from employee contract"""
        for record in self:
            if record.employee_id and record.employee_id.contract_id:
                record.basic_salary = record.employee_id.contract_id.wage
            else:
                # Get from config
                config_wage = self.env['ir.config_parameter'].sudo().get_param(
                    'hr_salary_advanced.basic_salary', '10000000'
                )
                try:
                    record.basic_salary = float(config_wage)
                except (ValueError, TypeError):
                    record.basic_salary = 10000000.0

    @api.depends('month', 'employee_id')
    def _compute_actual_days(self):
        """Count actual working days from attendance records"""
        for record in self:
            if not record.employee_id or not record.month:
                record.actual_days = 0
                continue

            try:
                year, month_num = map(int, record.month.split('-'))
                start_date = datetime(year, month_num, 1).date()
                if month_num == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month_num + 1, 1).date() - timedelta(days=1)
            except (ValueError, IndexError):
                record.actual_days = 0
                continue

            # Get attendance records
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', f'{start_date} 00:00:00'),
                ('check_in', '<=', f'{end_date} 23:59:59'),
            ])

            # Count distinct dates with attendance
            working_dates = set()
            for att in attendances:
                if att.check_in:
                    working_dates.add(att.check_in.date())

            record.actual_days = len(working_dates)

    @api.depends('actual_days', 'standard_days')
    def _compute_overtime_days(self):
        """Calculate overtime days"""
        for record in self:
            record.overtime_days = max(0, record.actual_days - record.standard_days)

    @api.depends('basic_salary', 'standard_days', 'actual_days')
    def _compute_salary_by_days(self):
        """
        Calculate salary by actual working days.
        
        Formula:
        - If actual_days <= standard_days: salary = (basic_salary / standard_days) × actual_days
        - If actual_days > standard_days: salary = basic_salary + (overtime_days × overtime_rate)
               (handled in _compute_overtime_bonus)
        """
        for record in self:
            if record.standard_days == 0:
                record.salary_by_days = 0
                continue

            if record.actual_days <= record.standard_days:
                daily_rate = record.basic_salary / record.standard_days
                record.salary_by_days = daily_rate * record.actual_days
            else:
                # Full salary (we add overtime separately)
                record.salary_by_days = record.basic_salary

    @api.depends('overtime_days', 'basic_salary')
    def _compute_overtime_bonus(self):
        """Calculate overtime bonus: overtime_days × 500k per day"""
        config = self.env['ir.config_parameter'].sudo()
        overtime_rate = float(config.get_param('hr_salary_advanced.overtime_rate', '500000'))

        for record in self:
            record.overtime_bonus = record.overtime_days * overtime_rate

    @api.depends('basic_salary')
    def _compute_total_insurance(self):
        """Calculate insurance: BHXH 8% + BHYT 1.5% + BHTN 1% = 10.5% of basic salary"""
        config = self.env['ir.config_parameter'].sudo()
        rate_bhxh = float(config.get_param('hr_salary_advanced.insurance_bhxh_rate', '0.08'))
        rate_bhyt = float(config.get_param('hr_salary_advanced.insurance_bhyt_rate', '0.015'))
        rate_bhtn = float(config.get_param('hr_salary_advanced.insurance_bhtn_rate', '0.01'))

        for record in self:
            total_rate = rate_bhxh + rate_bhyt + rate_bhtn
            record.total_insurance = record.basic_salary * total_rate

    @api.depends('month', 'employee_id')
    def _compute_late_penalty(self):
        """Calculate late penalty: total_late_minutes × 10000/minute"""
        config = self.env['ir.config_parameter'].sudo()
        penalty_per_minute = float(config.get_param('hr_salary_advanced.penalty_per_minute', '10000'))

        for record in self:
            if not record.employee_id or not record.month:
                record.late_penalty = 0
                continue

            try:
                year, month_num = map(int, record.month.split('-'))
                start_date = datetime(year, month_num, 1).date()
                if month_num == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month_num + 1, 1).date() - timedelta(days=1)
            except (ValueError, IndexError):
                record.late_penalty = 0
                continue

            # Get late attendance records
            late_records = self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', f'{start_date} 00:00:00'),
                ('check_in', '<=', f'{end_date} 23:59:59'),
                ('is_late', '=', True),
            ])

            total_late_minutes = sum(att.late_minutes for att in late_records)
            record.late_penalty = total_late_minutes * penalty_per_minute

    @api.depends('total_insurance', 'late_penalty')
    def _compute_total_deductions(self):
        """Total deductions = insurance + late penalty"""
        for record in self:
            record.total_deductions = record.total_insurance + record.late_penalty

    @api.depends('salary_by_days', 'overtime_bonus', 'total_deductions')
    def _compute_net_salary(self):
        """Net salary = salary_by_days + overtime_bonus - total_deductions"""
        for record in self:
            record.net_salary = record.salary_by_days + record.overtime_bonus - record.total_deductions

    # ===== ACTIONS =====

    def action_generate_lines(self):
        """Generate payslip line items"""
        for record in self:
            # Clear existing lines
            record.line_ids.unlink()

            lines_to_create = []

            # 1. Salary by days
            if record.salary_by_days > 0:
                lines_to_create.append({
                    'bang_luong_id': record.id,
                    'name': f'Lương Cơ Bản ({record.actual_days} ngày × {record.basic_salary/record.standard_days:,.0f})',
                    'amount': record.salary_by_days,
                    'type': 'cong',
                    'sequence': 10,
                    'description': f'({record.basic_salary:,.0f} / {record.standard_days}) × {record.actual_days}',
                })

            # 2. Overtime bonus
            if record.overtime_bonus > 0:
                lines_to_create.append({
                    'bang_luong_id': record.id,
                    'name': f'Thưởng Công Vượt ({record.overtime_days:.1f} ngày × 500k)',
                    'amount': record.overtime_bonus,
                    'type': 'cong',
                    'sequence': 20,
                    'description': f'{record.overtime_days:.1f} ngày × 500.000',
                })

            # 3. Insurance
            if record.total_insurance > 0:
                config = self.env['ir.config_parameter'].sudo()
                rate_bhxh = float(config.get_param('hr_salary_advanced.insurance_bhxh_rate', '0.08'))
                rate_bhyt = float(config.get_param('hr_salary_advanced.insurance_bhyt_rate', '0.015'))
                rate_bhtn = float(config.get_param('hr_salary_advanced.insurance_bhtn_rate', '0.01'))

                bhxh = record.basic_salary * rate_bhxh
                bhyt = record.basic_salary * rate_bhyt
                bhtn = record.basic_salary * rate_bhtn

                lines_to_create.append({
                    'bang_luong_id': record.id,
                    'name': 'Bảo Hiểm (BHXH, BHYT, BHTN)',
                    'amount': record.total_insurance,
                    'type': 'tru',
                    'sequence': 50,
                    'description': f'BHXH ({rate_bhxh*100}%): {bhxh:,.0f} + BHYT ({rate_bhyt*100}%): {bhyt:,.0f} + BHTN ({rate_bhtn*100}%): {bhtn:,.0f}',
                })

            # 4. Late penalty
            if record.late_penalty > 0:
                config = self.env['ir.config_parameter'].sudo()
                penalty_per_minute = float(config.get_param('hr_salary_advanced.penalty_per_minute', '10000'))

                total_late_minutes = record.late_penalty / penalty_per_minute
                lines_to_create.append({
                    'bang_luong_id': record.id,
                    'name': f'Phạt Đi Muộn ({int(total_late_minutes)} phút)',
                    'amount': record.late_penalty,
                    'type': 'tru',
                    'sequence': 60,
                    'description': f'{int(total_late_minutes)} phút × {penalty_per_minute:,.0f} VND/phút',
                })

            # Create all lines
            for line_data in lines_to_create:
                self.env['bang.luong.line'].create(line_data)

    def action_confirm(self):
        """Confirm payslip"""
        self.action_generate_lines()
        self.write({'state': 'done'})

    def action_cancel(self):
        """Cancel payslip"""
        self.write({'state': 'cancel'})

    def action_draft(self):
        """Back to draft"""
        self.write({'state': 'draft'})

    @api.model
    def create_payslip(self, employee_id, month):
        """Helper: create payslip for employee in specific month"""
        existing = self.search([
            ('employee_id', '=', employee_id),
            ('month', '=', month),
        ])
        if existing:
            return existing[0]

        return self.create({
            'employee_id': employee_id,
            'month': month,
        })
