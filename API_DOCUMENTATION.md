# API DOCUMENTATION - Modules Chấm Công & Tính Lương

## Mục lục

1. [API hr_attendance_penalty](#api-hr_attendance_penalty)
2. [API hr_salary_custom](#api-hr_salary_custom)
3. [Ví dụ sử dụng](#ví-dụ-sử-dụng)
4. [Mở rộng & tùy chỉnh](#mở-rộng--tùy-chỉnh)

---

## API hr_attendance_penalty

### Model: `hr.attendance`

#### Fields

| Field | Type | Attributes | Mô tả |
|-------|------|-----------|-------|
| `is_late` | Boolean | readonly, store | Đánh dấu đi muộn |
| `late_minutes` | Integer | readonly, store | Số phút muộn (làm tròn lên) |

#### Methods

##### `_compute_late_check_in()`
```python
def _compute_late_check_in(self):
    """
    Tính toán xem nhân viên có đi muộn không.
    Gọi tự động khi create/write attendance.
    
    Logic:
    - So sánh check_in với giờ chuẩn
    - Nếu check_in > giờ_chuẩn: is_late = True
    - Tính late_minutes = (check_in - giờ_chuẩn) / 60
    """
```

##### `_get_standard_check_in_time(employee)`
```python
def _get_standard_check_in_time(self, employee):
    """
    Lấy giờ chuẩn check-in.
    
    Args:
        employee (hr.employee): Nhân viên
        
    Returns:
        datetime.time: Giờ chuẩn (VD: time(8, 30))
        
    Thứ tự ưu tiên:
    1. Từ cấu hình parameter
    2. Mặc định 08:30
    """
```

#### Config Parameters

| Parameter | Type | Default | Mô tả |
|-----------|------|---------|-------|
| `hr_attendance_penalty.standard_check_in_time` | string | '08:30' | Giờ chuẩn (HH:MM) |

#### Ví dụ sử dụng

```python
# Lấy tất cả attendance đi muộn trong tháng 1/2024
from odoo import fields
from datetime import datetime

attendances = self.env['hr.attendance'].search([
    ('check_in', '>=', '2024-01-01'),
    ('check_in', '<', '2024-02-01'),
    ('is_late', '=', True),
])

# Tính tổng phút muộn
total_late_minutes = sum(att.late_minutes for att in attendances)
print(f"Tổng phút muộn: {total_late_minutes}")

# Tìm nhân viên đi muộn nhiều nhất
for att in attendances:
    print(f"Nhân viên {att.employee_id.name}: {att.late_minutes} phút muộn")
```

---

## API hr_salary_custom

### Model: `bang.luong` (Phiếu lương)

#### Fields

| Field | Type | Attributes | Mô tả |
|-------|------|-----------|-------|
| `employee_id` | Many2one | required | Liên kết nhân viên |
| `month` | Char | required | Tháng (YYYY-MM) |
| `line_ids` | One2many | copy | Chi tiết lương |
| `tong_cong` | Float | computed, store | Tổng tiền cộng |
| `tong_tru` | Float | computed, store | Tổng tiền trừ |
| `thuc_lanh` | Float | computed, store | Lương thực lãnh |
| `state` | Selection | - | Trạng thái (draft/done/cancel) |
| `notes` | Text | - | Ghi chú |

#### Methods

##### `action_generate_lines()`
```python
def action_generate_lines(self):
    """
    Tự động sinh các dòng lương.
    
    Quy trình:
    1. Xóa các dòng cũ
    2. Lấy lương cơ bản từ hợp đồng
    3. Tính phạt đi muộn
    4. Thêm các khoản khác
    5. Tạo tất cả dòng vào CSDL
    
    Ví dụ:
        bang_luong = self.env['bang.luong'].browse(1)
        bang_luong.action_generate_lines()
    """
```

##### `_get_luong_co_ban()`
```python
def _get_luong_co_ban(self):
    """
    Lấy lương cơ bản từ hợp đồng hoặc config.
    
    Returns:
        dict: {
            'bang_luong_id': self.id,
            'name': 'Lương cơ bản',
            'amount': 10000000,
            'type': 'cong',
            'sequence': 10,
            'description': '...'
        }
        
    Thứ tự ưu tiên:
    1. contract.wage (nếu có hợp đồng)
    2. Config default_wage
    3. None (nếu cả hai là 0)
    """
```

##### `_calculate_phat_lines()`
```python
def _calculate_phat_lines(self):
    """
    Tính các khoản phạt dựa trên attendance.
    
    Returns:
        list: Danh sách dict, mỗi cái là một dòng phạt
        
    Logic:
    1. Lấy tất cả attendance trong tháng
    2. Tính tổng late_minutes
    3. Nhân với mức phạt/phút từ config
    4. Trả về danh sách dòng với type='tru'
    """
```

##### `action_confirm()`
```python
def action_confirm(self):
    """
    Xác nhận phiếu lương → Chuyển state từ 'draft' → 'done'
    """
```

##### `action_cancel()`
```python
def action_cancel(self):
    """
    Hủy phiếu lương → state = 'cancel'
    """
```

##### `action_draft()`
```python
def action_draft(self):
    """
    Quay lại bản nháp → state = 'draft'
    """
```

##### `create_payslips_for_month(employee_id, month)`
```python
@api.model
def create_payslips_for_month(self, employee_id, month):
    """
    Tạo phiếu lương cho nhân viên trong tháng.
    
    Args:
        employee_id (int): ID nhân viên
        month (str): Tháng (YYYY-MM)
        
    Returns:
        bang.luong: Record phiếu lương vừa tạo
        
    Ví dụ:
        payslip = self.env['bang.luong'].create_payslips_for_month(
            employee_id=1,
            month='2024-01'
        )
    """
```

#### Computed Fields

##### `tong_cong`
```python
# Tính tổng các dòng có type='cong'
tong_cong = sum(line.amount for line in line_ids if line.type == 'cong')
```

##### `tong_tru`
```python
# Tính tổng các dòng có type='tru'
tong_tru = sum(line.amount for line in line_ids if line.type == 'tru')
```

##### `thuc_lanh`
```python
# Tính lương thực lãnh
thuc_lanh = tong_cong - tong_tru
```

---

### Model: `bang.luong.line` (Chi tiết phiếu lương)

#### Fields

| Field | Type | Attributes | Mô tả |
|-------|------|-----------|-------|
| `bang_luong_id` | Many2one | required, cascade | Phiếu lương cha |
| `name` | Char | required | Nội dung khoản lương |
| `amount` | Float | required | Số tiền |
| `type` | Selection | required | Loại [('cong', 'Cộng'), ('tru', 'Trừ')] |
| `sequence` | Integer | - | Thứ tự hiển thị |
| `description` | Text | - | Ghi chú chi tiết |

#### Không có methods đặc biệt

---

#### Config Parameters

| Parameter | Type | Default | Mô tả |
|-----------|------|---------|-------|
| `hr_salary_custom.penalty_per_minute` | float | 1000 | Phạt đi muộn (VND/phút) |
| `hr_salary_custom.default_wage` | float | 0 | Lương cơ bản mặc định |
| `hr_salary_custom.penalty_early_checkout` | float | 500 | Phạt về sớm (VND/phút) |

---

## Ví dụ sử dụng

### Ví dụ 1: Tạo phiếu lương qua Python

```python
# Trong method hoặc scheduled action
payslip = self.env['bang.luong'].create({
    'employee_id': 1,  # ID nhân viên
    'month': '2024-01'  # Tháng
})

# Tính lương tự động
payslip.action_generate_lines()

# Xem chi tiết
print(f"Tổng cộng: {payslip.tong_cong}")
print(f"Tổng trừ: {payslip.tong_tru}")
print(f"Thực lãnh: {payslip.thuc_lanh}")

# Xác nhận
payslip.action_confirm()
```

### Ví dụ 2: Lấy danh sách nhân viên đi muộn

```python
from datetime import datetime

# Lấy tất cả attendance đi muộn
late_attendances = self.env['hr.attendance'].search([
    ('is_late', '=', True),
    ('check_in', '>=', '2024-01-01'),
    ('check_in', '<', '2024-02-01'),
])

# Nhóm theo nhân viên
from collections import defaultdict
by_employee = defaultdict(list)
for att in late_attendances:
    by_employee[att.employee_id].append(att)

# In báo cáo
for employee, attendances in by_employee.items():
    total_late = sum(att.late_minutes for att in attendances)
    print(f"{employee.name}: {total_late} phút muộn")
```

### Ví dụ 3: Tính lương cho tất cả nhân viên trong tháng

```python
# Scheduled action hoặc method
def calculate_monthly_payslips(self, month):
    """
    Tính lương cho tất cả nhân viên trong tháng.
    month: '2024-01'
    """
    employees = self.env['hr.employee'].search([
        ('contract_ids', '!=', False)
    ])
    
    payslips = []
    for employee in employees:
        payslip = self.env['bang.luong'].create_payslips_for_month(
            employee_id=employee.id,
            month=month
        )
        payslips.append(payslip)
    
    return payslips
```

### Ví dụ 4: Thêm custom logic vào lương

```python
# Override method để mở rộng logic
class BangLuong(models.Model):
    _inherit = 'bang.luong'
    
    def _calculate_phat_lines(self):
        """
        Override để thêm phạt về sớm
        """
        lines = super()._calculate_phat_lines()
        
        # Thêm logic phạt về sớm
        phat_ve_som = self._calculate_early_checkout_penalty()
        lines.extend(phat_ve_som)
        
        # Thêm thưởng hiệu suất
        thuong = self._calculate_performance_bonus()
        lines.extend(thuong)
        
        return lines
    
    def _calculate_early_checkout_penalty(self):
        """Tính phạt về sớm"""
        # Logic tính toán...
        pass
    
    def _calculate_performance_bonus(self):
        """Tính thưởng hiệu suất"""
        # Logic tính toán...
        pass
```

---

## Mở rộng & tùy chỉnh

### 1. Thêm logic phạt về sớm

**File**: `addons/hr_salary_custom/models/bang_luong.py`

```python
def _calculate_phat_lines(self):
    """Override method để thêm phạt về sớm"""
    self.ensure_one()
    lines = []

    if not self.employee_id or not self.month:
        return lines

    # ... (code cũ cho phạt đi muộn) ...
    
    # THÊM: Tính phạt về sớm
    phat_ve_som = self._calculate_early_checkout()
    lines.extend(phat_ve_som)
    
    return lines

def _calculate_early_checkout(self):
    """Tính phạt về sớm"""
    # Logic tương tự như phạt đi muộn
    # Sử dụng config: penalty_early_checkout
    pass
```

### 2. Tính thưởng dựa trên doanh số

```python
def _calculate_phat_lines(self):
    """Thêm logic thưởng"""
    lines = super()._calculate_phat_lines()
    
    # Lấy doanh số từ module sale
    sale_orders = self.env['sale.order'].search([
        ('user_id', '=', self.employee_id.user_id.id),
        ('date_order', '>=', f'{self.month}-01'),
        ('date_order', '<', f'{self.month}-32'),  # Lấy tất cả ngày trong tháng
        ('state', 'in', ['sale', 'done'])
    ])
    
    total_amount = sum(so.amount_total for so in sale_orders)
    
    # Tính thưởng: 2% doanh số
    if total_amount > 0:
        commission = total_amount * 0.02
        lines.append({
            'bang_luong_id': self.id,
            'name': 'Hoa hồng bán hàng',
            'amount': commission,
            'type': 'cong',
            'sequence': 20,
            'description': f'Hoa hồng 2% doanh số: {total_amount:,.0f}'
        })
    
    return lines
```

### 3. Tạo report xuất lương

```python
# File: addons/hr_salary_custom/report/payslip_report.py

from odoo import models

class PayslipReport(models.Model):
    _name = 'report.hr_salary_custom.payslip_template'
    _description = 'Báo cáo phiếu lương'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env['bang.luong'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'bang.luong',
            'docs': payslips,
        }
```

### 4. Tạo Scheduled Action tính lương hằng tháng

```python
# XML: views/bank_luong_views.xml

<record id="ir_cron_monthly_payslip" model="ir.cron">
    <field name="name">Tính lương tháng</field>
    <field name="model_id" ref="model_bang_luong" />
    <field name="state">code</field>
    <field name="code">
env['bang.luong'].auto_create_monthly_payslips()
    </field>
    <field name="interval_number">1</field>
    <field name="interval_type">months</field>
    <field name="nextcall">2024-02-01 00:00:00</field>
</record>
```

---

## Integration Points

### Tích hợp với module sale (hoa hồng)
- Lấy dữ liệu từ `sale.order`
- Tính commission dựa trên tổng doanh số

### Tích hợp với module expense (chi phí nhân viên)
- Lấy dữ liệu từ `hr.expense`
- Trừ chi phí từ lương

### Tích hợp với module account (kế toán)
- Xuất journal entry khi xác nhận phiếu lương
- Tạo bill cho lương trả

---

## Best Practices

1. **Validate dữ liệu**: Luôn kiểm tra employee_id, month trước khi tính lương
2. **Handle edge cases**: 
   - Nhân viên không có hợp đồng
   - Tháng không hợp lệ
   - Attendance trống
3. **Lưu trữ logs**: Ghi lại mỗi lần tính lương cho audit
4. **Performance**: 
   - Sử dụng `search()` với limit nếu có nhiều records
   - Cache config parameters
5. **Security**: Kiểm tra quyền truy cập trước khi xem phiếu lương

---

**Phiên bản**: 1.0  
**Cập nhật**: 2024  
**Hỗ trợ**: Odoo 15, 16+
