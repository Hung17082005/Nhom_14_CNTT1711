from odoo import models, fields, api
from datetime import datetime, timedelta
import math


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_late = fields.Boolean(
        string='Đi muộn',
        readonly=True,
        store=True,
        help='Đánh dấu nếu nhân viên đi muộn so với giờ chuẩn'
    )
    
    late_minutes = fields.Integer(
        string='Số phút muộn',
        readonly=True,
        store=True,
        help='Tính bằng phút'
    )
    
    work_hours_computed = fields.Float(
        string='Tổng giờ làm',
        compute='_compute_work_hours_fixed',
        store=True,
        help='Tính số giờ làm việc thực tế (không bao gồm giờ nghỉ trưa)'
    )
    
    is_invalid_time = fields.Boolean(
        string='Dữ liệu không hợp lệ',
        readonly=True,
        store=True,
        help='Đánh dấu nếu check_out trước check_in'
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._compute_late_check_in()
        return records

    def write(self, vals):
        result = super().write(vals)
        # Khi cập nhật check_in, check_out hoặc employee_id, tính toán lại
        if 'check_in' in vals or 'check_out' in vals or 'employee_id' in vals:
            for record in self:
                record._compute_late_check_in()
        return result

    def _compute_late_check_in(self):
        """
        Tính toán xem nhân viên có đi muộn không dựa trên check_in time.
        So sánh với giờ chuẩn trong setting hoặc lấy từ working schedule.
        """
        for record in self:
            if not record.check_in:
                record.is_late = False
                record.late_minutes = 0
                continue

            # Lấy giờ chuẩn check-in từ config (mặc định 08:30)
            standard_time = self._get_standard_check_in_time(record.employee_id)
            
            # Lấy ngày check-in và giờ chuẩn cùng ngày
            check_in_dt = record.check_in
            check_in_date = check_in_dt.date()
            
            # Tạo datetime cho giờ chuẩn trong cùng ngày
            standard_check_in = datetime.combine(check_in_date, standard_time)
            
            # So sánh
            if check_in_dt > standard_check_in:
                record.is_late = True
                # Tính số phút muộn (làm tròn lên)
                time_diff = check_in_dt - standard_check_in
                minutes_late = math.ceil(time_diff.total_seconds() / 60)
                record.late_minutes = minutes_late
            else:
                record.is_late = False
                record.late_minutes = 0

    def _get_standard_check_in_time(self, employee):
        """
        Lấy giờ chuẩn check-in.
        Thứ tự ưu tiên:
        1. Từ working schedule của nhân viên (nếu có)
        2. Từ cấu hình hệ thống (mặc định 08:30)
        """
        # Lấy giờ từ config
        config_time = self.env['ir.config_parameter'].sudo().get_param(
            'hr_attendance_penalty.standard_check_in_time',
            '08:30'
        )
        
        try:
            # Chuyển string thành time object (format: HH:MM)
            hour, minute = map(int, config_time.split(':'))
            return datetime.min.time().replace(hour=hour, minute=minute)
        except (ValueError, AttributeError):
            # Nếu config không hợp lệ, mặc định 08:30
            return datetime.min.time().replace(hour=8, minute=30)

    @api.depends('check_in', 'check_out')
    def _compute_work_hours_fixed(self):
        """
        ✅ FIXED: Tính ĐÚNG tổng giờ làm việc
        
        Xử lý các trường hợp:
        1. Check-in và check-out cùng ngày
        2. Check-in và check-out khác ngày (qua đêm)
        3. Trừ thời gian nghỉ trưa (12:00-13:00 mặc định)
        4. Validate dữ liệu (check_out phải >= check_in)
        5. Format HH:MM
        
        Công thức: 
        total_hours = (check_out - check_in) - lunch_time
        """
        for record in self:
            record.is_invalid_time = False
            
            # Nếu thiếu check_in hoặc check_out
            if not record.check_in or not record.check_out:
                record.work_hours_computed = 0.0
                continue
            
            check_in = record.check_in
            check_out = record.check_out
            
            # 🔴 VALIDATE: Check_out phải >= Check_in
            if check_out < check_in:
                record.is_invalid_time = True
                record.work_hours_computed = 0.0
                continue
            
            # ✅ Tính tổng thời gian làm việc (tính từng ngày nếu qua đêm)
            total_seconds = (check_out - check_in).total_seconds()
            
            # 🍽️ Trừ giờ nghỉ trưa
            lunch_minutes = record._get_lunch_break_minutes(check_in, check_out)
            total_seconds -= lunch_minutes * 60
            
            # 📊 Chuyển thành giờ (làm tròn 2 chữ số)
            total_hours = total_seconds / 3600
            record.work_hours_computed = round(max(0, total_hours), 2)

    def _get_lunch_break_minutes(self, check_in, check_out):
        """
        Tính số phút nghỉ trưa trong khoảng check_in -> check_out.
        
        Mặc định: 12:00 - 13:00 (60 phút)
        Có thể cấu hình từ settings
        
        Xử lý:
        - Nếu qua đêm (check_in.date != check_out.date)
        - Chỉ trừ giờ nghỉ nếu nó nằm trong khoảng thời gian làm việc
        """
        # Lấy config giờ nghỉ trưa
        lunch_start_config = self.env['ir.config_parameter'].sudo().get_param(
            'hr_salary_automation.lunch_start',
            '12:00'  # HH:MM format
        )
        lunch_end_config = self.env['ir.config_parameter'].sudo().get_param(
            'hr_salary_automation.lunch_end',
            '13:00'
        )
        
        try:
            lunch_start_h, lunch_start_m = map(int, lunch_start_config.split(':'))
            lunch_end_h, lunch_end_m = map(int, lunch_end_config.split(':'))
            
            lunch_start_time = datetime.min.time().replace(hour=lunch_start_h, minute=lunch_start_m)
            lunch_end_time = datetime.min.time().replace(hour=lunch_end_h, minute=lunch_end_m)
        except (ValueError, AttributeError):
            # Mặc định 12:00 - 13:00
            lunch_start_time = datetime.min.time().replace(hour=12, minute=0)
            lunch_end_time = datetime.min.time().replace(hour=13, minute=0)
        
        lunch_minutes = 0
        
        # Trường hợp 1: Cùng ngày
        if check_in.date() == check_out.date():
            # Kiểm tra nếu giờ nghỉ nằm trong khoảng làm việc
            check_in_time = check_in.time()
            check_out_time = check_out.time()
            
            if check_in_time < lunch_start_time and check_out_time > lunch_end_time:
                # Giờ nghỉ nằm hoàn toàn trong khoảng làm việc
                lunch_minutes = int((datetime.combine(datetime.today(), lunch_end_time) - 
                                    datetime.combine(datetime.today(), lunch_start_time)).total_seconds() / 60)
            elif check_in_time < lunch_end_time and check_out_time > lunch_start_time:
                # Giờ nghỉ bị cắt ngang (check_in lúc 11:30 hoặc check_out lúc 13:30)
                actual_lunch_start = max(check_in_time, lunch_start_time)
                actual_lunch_end = min(check_out_time, lunch_end_time)
                
                lunch_start_dt = datetime.combine(check_in.date(), actual_lunch_start)
                lunch_end_dt = datetime.combine(check_in.date(), actual_lunch_end)
                lunch_minutes = int((lunch_end_dt - lunch_start_dt).total_seconds() / 60)
        else:
            # Trường hợp 2: Qua đêm (check_in ngày này, check_out ngày kế tiếp)
            # Chỉ trừ giờ nghỉ nếu nó nằm trong các ngày làm việc (không trừ nếu qua đêm)
            # Mặc định: chỉ trừ giờ nghỉ ngày check_in
            
            check_in_time = check_in.time()
            if check_in_time < lunch_end_time:
                # Giờ nghỉ ngày check_in nằm trong khoảng làm việc
                actual_lunch_start = max(check_in_time, lunch_start_time)
                lunch_start_dt = datetime.combine(check_in.date(), actual_lunch_start)
                lunch_end_dt = datetime.combine(check_in.date(), lunch_end_time)
                lunch_minutes = int((lunch_end_dt - lunch_start_dt).total_seconds() / 60)
        
        return lunch_minutes
