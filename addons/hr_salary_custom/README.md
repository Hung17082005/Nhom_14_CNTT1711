# HR Salary Custom - Module Tính lương tự động

## Mô tả
Module này cung cấp chức năng tính lương tự động cho nhân viên, bao gồm:
- Lương cơ bản từ hợp đồng
- Phạt đi muộn (tự động tính từ attendance records)
- Phạt về sớm (tùy chọn)
- Các khoản thưởng (có thể mở rộng)

## Tính năng chính

### 1. Model `bang.luong` (Phiếu lương)
Lưu trữ thông tin phiếu lương tháng của nhân viên.

**Fields chính**:
- `employee_id` (Many2one): Nhân viên
- `month` (Char): Tháng tính lương (format: YYYY-MM)
- `line_ids` (One2many): Danh sách chi tiết lương
- `state` (Selection): Trạng thái (draft/done/cancel)
- `tong_cong` (Float - computed): Tổng tiền cộng
- `tong_tru` (Float - computed): Tổng tiền trừ
- `thuc_lanh` (Float - computed): Lương thực lãnh = Tổng cộng - Tổng trừ

### 2. Model `bang.luong.line` (Chi tiết phiếu lương)
Mỗi dòng lương (lương cứng, thưởng, phạt, v.v.)

**Fields chính**:
- `bang_luong_id` (Many2one): Phiếu lương cha
- `name` (Char): Nội dung (VD: "Lương cứng", "Phạt đi muộn")
- `amount` (Float): Số tiền
- `type` (Selection): Loại [('cong', 'Cộng'), ('tru', 'Trừ')]
- `sequence` (Integer): Thứ tự sắp xếp
- `description` (Text): Ghi chú chi tiết

### 3. Logic tự động sinh phiếu lương

Method `action_generate_lines()` tự động tạo các dòng lương:

#### a. Lương cơ bản
- Lấy từ `hr.employee.contract_id.wage`
- Nếu không có hợp đồng, lấy từ config parameter `default_wage`

#### b. Phạt đi muộn
- Tính tổng số phút đi muộn trong tháng từ `hr.attendance.late_minutes`
- Nhân với mức phạt/phút (config: `penalty_per_minute`)
- Tạo dòng với type='tru' (trừ)

#### c. Phạt về sớm (tùy chọn)
- Tương tự như phạt đi muộn
- Mức phạt: config `penalty_early_checkout`

### 4. Cấu hình

Tất cả cấu hình nằm tại **Cài đặt > Tính lương tự động**:

| Parameter | Giá trị mặc định | Mô tả |
|-----------|-----------------|-------|
| `standard_check_in_time` | 08:30 | Giờ chuẩn check-in (HH:MM) |
| `penalty_per_minute` | 1000 | Phạt đi muộn (VND/phút) |
| `penalty_early_checkout` | 500 | Phạt về sớm (VND/phút) |
| `default_wage` | 0 | Lương cơ bản mặc định (VND) |

## Cài đặt vào Odoo

1. Sao chép thư mục `hr_salary_custom/` vào `addons/`
2. Trong terminal, chạy:
   ```bash
   ./odoo-bin --addons-path=addons -d <database_name> -u hr_salary_custom
   ```
3. Hoặc tại giao diện Odoo: **Ứng dụng > Cập nhật danh sách modules** > Tìm `HR Salary Custom` > Cài đặt

## Sử dụng

### 1. Cấu hình ban đầu
- Truyển đến **Cài đặt > Tính lương tự động**
- Điền:
  - Giờ chuẩn check-in (VD: 08:30)
  - Mức phạt đi muộn (VD: 1000 VND/phút)
  - Lương cơ bản mặc định
- Nhấn **Lưu**

### 2. Tạo phiếu lương cho nhân viên trong tháng
- Truyển đến **Nhân sự > Phiếu lương** (hoặc **Tính lương > Phiếu lương**)
- Nhấn **Tạo mới**
- Điền:
  - **Nhân viên**: Chọn nhân viên
  - **Tháng**: Nhập tháng (format: YYYY-MM, VD: 2024-01)
- Nhấn **Tính lương** → Hệ thống tự động sinh các dòng lương

### 3. Xem chi tiết phiếu lương
- Tab **"Chi tiết lương"**: Hiển thị tất cả khoản lương (dạng editable)
- Có thể thêm/sửa/xóa các dòng lương tùy ý
- Các trường computed (`tong_cong`, `tong_tru`, `thuc_lanh`) tự động cập nhật

### 4. Xác nhận phiếu lương
- Nhấn **Xác nhận** → Chuyển trạng thái từ "Bản nháp" → "Hoàn tất"
- Sau khi xác nhận, có thể:
  - Nhấn **Quay lại bản nháp** (để chỉnh sửa lại)
  - Nhấn **Hủy** (để hủy phiếu lương)

## Code Structure

```
hr_salary_custom/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── bang_luong.py           # Model phiếu lương
│   ├── bang_luong_line.py      # Model chi tiết lương
│   └── config_settings.py      # Settings & config
└── views/
    ├── __init__.py
    ├── bang_luong_views.xml    # Views cho bang.luong & bang.luong.line
    └── config_settings_views.xml # Settings view
```

## Ví dụ thực tế

### Tính lương cho tháng 1/2024:

**Nhân viên**: Nguyễn Văn A
**Tháng**: 2024-01

**Dòng lương tự động sinh**:
1. Lương cứng: 10,000,000 VND (Cộng)
2. Phạt đi muộn: -120,000 VND (Trừ)
   - 120 phút đi muộn × 1,000 VND/phút

**Kết quả**:
- Tổng cộng: 10,000,000
- Tổng trừ: 120,000
- **Thực lãnh: 9,880,000 VND**

---

### Mở rộng logic (có thể tùy chỉnh)

Module được thiết kế để dễ mở rộng:

1. **Thêm các khoản thưởng**: Sửa method `_calculate_phat_lines()` thành `_calculate_salary_adjustments()`
2. **Tính tổng giờ làm việc**: Thêm logic dựa trên `worked_hours` từ attendance
3. **Hoa hồng theo doanh số**: Thêm model bán hàng và tích hợp với lương

---

## Dependencies
- hr_attendance
- hr_contract
- hr (base)
- hr_attendance_penalty (module chấm công)

## Hỗ trợ Odoo
- Odoo 15.0+
- Odoo 16.0+

## Contact
- Để báo cáo lỗi hoặc đề xuất tính năng, vui lòng liên hệ
