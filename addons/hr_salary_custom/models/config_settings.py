from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """
    Cấu hình tính lương và chấm công.
    """
    _inherit = 'res.config.settings'

    # Giờ chuẩn check-in (format HH:MM)
    standard_check_in_time = fields.Char(
        string='Giờ chuẩn check-in',
        default='08:30',
        help='Định dạng HH:MM (ví dụ: 08:30, 09:00)'
    )

    # Mức phạt đi muộn (VND/phút)
    penalty_per_minute = fields.Float(
        string='Mức phạt đi muộn (VND/phút)',
        default=1000.0,
        help='Số tiền phạt cho mỗi phút đi muộn'
    )

    # Lương cơ bản mặc định (nếu không có hợp đồng)
    default_wage = fields.Float(
        string='Lương cơ bản mặc định (VND)',
        default=0.0,
        help='Sử dụng khi nhân viên không có hợp đồng'
    )

    # Phạt về sớm (VND/phút)
    penalty_early_checkout = fields.Float(
        string='Mức phạt về sớm (VND/phút)',
        default=500.0,
        help='Số tiền phạt cho mỗi phút về sớm (nếu cần)'
    )

    # ✅ NEW: GIỜ NGHỈ TRƯA
    lunch_start = fields.Char(
        string='Giờ bắt đầu nghỉ trưa',
        default='12:00',
        help='Định dạng HH:MM (ví dụ: 12:00)'
    )

    lunch_end = fields.Char(
        string='Giờ kết thúc nghỉ trưa',
        default='13:00',
        help='Định dạng HH:MM (ví dụ: 13:00)'
    )

    # ✅ NEW: BẢOIỂM
    insurance_bhxh_rate = fields.Float(
        string='Tỷ lệ BHXH (%)',
        default=8.0,
        help='Tỷ lệ bảo hiểm xã hội (%, VD: 8 = 8%)'
    )

    insurance_bhyt_rate = fields.Float(
        string='Tỷ lệ BHYT (%)',
        default=1.5,
        help='Tỷ lệ bảo hiểm y tế (%, VD: 1.5 = 1.5%)'
    )

    insurance_bhtn_rate = fields.Float(
        string='Tỷ lệ BHTN (%)',
        default=1.0,
        help='Tỷ lệ bảo hiểm thất nghiệp (%, VD: 1 = 1%)'
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'standard_check_in_time': params.get_param(
                'hr_attendance_penalty.standard_check_in_time', '08:30'
            ),
            'penalty_per_minute': float(params.get_param(
                'hr_salary_custom.penalty_per_minute', '1000'
            )),
            'default_wage': float(params.get_param(
                'hr_salary_custom.default_wage', '0'
            )),
            'penalty_early_checkout': float(params.get_param(
                'hr_salary_custom.penalty_early_checkout', '500'
            )),
            'lunch_start': params.get_param(
                'hr_salary_automation.lunch_start', '12:00'
            ),
            'lunch_end': params.get_param(
                'hr_salary_automation.lunch_end', '13:00'
            ),
            'insurance_bhxh_rate': float(params.get_param(
                'hr_salary_custom.insurance_bhxh_rate', '8.0'
            )) / 100,  # Chuyển từ % sang decimal
            'insurance_bhyt_rate': float(params.get_param(
                'hr_salary_custom.insurance_bhyt_rate', '1.5'
            )) / 100,
            'insurance_bhtn_rate': float(params.get_param(
                'hr_salary_custom.insurance_bhtn_rate', '1.0'
            )) / 100,
        })
        return res

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            'hr_attendance_penalty.standard_check_in_time',
            self.standard_check_in_time or '08:30'
        )
        params.set_param(
            'hr_salary_custom.penalty_per_minute',
            str(self.penalty_per_minute or 1000)
        )
        params.set_param(
            'hr_salary_custom.default_wage',
            str(self.default_wage or 0)
        )
        params.set_param(
            'hr_salary_custom.penalty_early_checkout',
            str(self.penalty_early_checkout or 500)
        )
        params.set_param(
            'hr_salary_automation.lunch_start',
            self.lunch_start or '12:00'
        )
        params.set_param(
            'hr_salary_automation.lunch_end',
            self.lunch_end or '13:00'
        )
        params.set_param(
            'hr_salary_custom.insurance_bhxh_rate',
            str((self.insurance_bhxh_rate or 0.08) * 100)  # Chuyển từ decimal sang %
        )
        params.set_param(
            'hr_salary_custom.insurance_bhyt_rate',
            str((self.insurance_bhyt_rate or 0.015) * 100)
        )
        params.set_param(
            'hr_salary_custom.insurance_bhtn_rate',
            str((self.insurance_bhtn_rate or 0.01) * 100)
        )
