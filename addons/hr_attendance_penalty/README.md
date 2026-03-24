# HR Attendance Penalty - Module Chấm công với xác định đi muộn

## Mô tả
Module này mở rộng chức năng của `hr.attendance` (Chấm công) để tự động xác định và ghi lại nhân viên đi muộn.

## Tính năng chính

### 1. Tự động xác định đi muộn
- **Fields mới**:
  - `is_late` (Boolean): Đánh dấu xem nhân viên có đi muộn hay không
  - `late_minutes` (Integer): Số phút đi muộn (làm tròn lên)

### 2. Logic tính toán
- Khi nhân viên check-in, hệ thống tự động so sánh `check_in` time với **giờ chuẩn** được cấu hình
- Nếu `check_in > giờ_chuẩn`:
  - Set `is_late = True`
  - Tính `late_minutes` = sự chênh lệch (đơn vị: phút)

### 3. Cấu hình
Giờ chuẩn check-in được lấy từ:
1. **Config parameter**: `hr_attendance_penalty.standard_check_in_time` (format: HH:MM)
2. Mặc định: `08:30`

### 4. Views
- **Tree View**: Hiển thị danh sách chấm công với màu đỏ (danger) cho những người đi muộn
- **Search Filters**: Lọc theo "Đi muộn" hoặc "Không muộn"

## Cài đặt vào Odoo

1. Sao chép thư mục `hr_attendance_penalty/` vào `addons/`
2. Cập nhật danh sách modules: **Ứng dụng > Cập nhật danh sách modules**
3. Tìm và cài đặt `HR Attendance Penalty`

## Sử dụng

### 1. Thêm nhân viên chấm công
- Chuyển đến **Nhân sự > Chấm công**
- Thêm record check-in/check-out bình thường

### 2. Xem danh sách đi muộn
- Tree view tự động hiệu chỉnh `is_late` và `late_minutes`
- Các dòng có `is_late = True` sẽ hiển thị với màu đỏ

### 3. Cấu hình giờ chuẩn
- Truyển đến **Cài đặt > Tính lương tự động** (Settings)
- Chỉnh sửa **"Giờ chuẩn check-in"** (format: HH:MM)
- Lưu lại

## Code Structure

```
hr_attendance_penalty/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── hr_attendance.py    # Extends hr.attendance
└── views/
    ├── __init__.py
    └── hr_attendance_views.xml
```

## Ví dụ

**Tình huống 1**: Giờ chuẩn = 08:30
- Nhân viên check-in lúc 08:45
- `is_late` = True
- `late_minutes` = 15

**Tình huống 2**: Giờ chuẩn = 08:30
- Nhân viên check-in lúc 08:20
- `is_late` = False
- `late_minutes` = 0

---

## Technical Notes

- Các fields `is_late` và `late_minutes` được tính toán trong method `_compute_late_check_in()`
- Hàm được gọi khi tạo mới (create) hoặc cập nhật (write) attendance record
- Hỗ trợ Odoo 15, 16+
