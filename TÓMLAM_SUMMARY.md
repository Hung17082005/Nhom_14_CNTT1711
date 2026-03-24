# TÓMLAM TẢT CÁC FILE ĐÃ TẠO

## 📁 Cấu trúc Thư mục

```
/home/hung/16-06-N11/
├── addons/
│   ├── hr_attendance_penalty/              # Module xác định đi muộn
│   │   ├── __init__.py
│   │   ├── __manifest__.py                 # Manifest (phiên bản, dependencies)
│   │   ├── README.md                        # Tài liệu chi tiết
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── hr_attendance.py            # Extend hr.attendance model
│   │   └── views/
│   │       ├── __init__.py
│   │       └── hr_attendance_views.xml    # Tree/Form views, filters
│   │
│   ├── hr_salary_custom/                   # Module tính lương
│   │   ├── __init__.py
│   │   ├── __manifest__.py                 # Manifest (phiên bản, dependencies)
│   │   ├── README.md                        # Tài liệu chi tiết
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── bang_luong.py               # Model phiếu lương (cha)
│   │   │   ├── bang_luong_line.py          # Model chi tiết lương (con)
│   │   │   └── config_settings.py          # Settings & config
│   │   └── views/
│   │       ├── __init__.py
│   │       ├── bang_luong_views.xml        # Views cho bang.luong & line
│   │       └── config_settings_views.xml  # Settings view
│   │
│   └── ... (modules khác của Odoo)
│
├── HƯỚNG_DẪN_SỬ_DỤNG.md                    # Hướng dẫn cho người dùng cuối
├── API_DOCUMENTATION.md                    # Tài liệu API cho lập trình viên
├── CHANGELOG.md                            # Lịch sử thay đổi
└── ...

```

---

## 📄 File Quan Trọng & Nội dung

### 1. hr_attendance_penalty

#### hr_attendance_penalty/__manifest__.py
- **Mục đích**: Khai báo module, dependencies, data files
- **Nội dung chính**:
  - name: "HR Attendance Penalty"
  - depends: ['hr_attendance', 'hr_contract']
  - data: ['views/hr_attendance_views.xml']

#### hr_attendance_penalty/models/hr_attendance.py
- **Mục đích**: Extends model `hr.attendance` để thêm fields và logic
- **Nội dung chính**:
  - Fields: `is_late`, `late_minutes`
  - Method: `_compute_late_check_in()` - tính toán đi muộn
  - Method: `_get_standard_check_in_time()` - lấy giờ chuẩn từ config
  - Create/write hooks gọi tự động tính toán

#### hr_attendance_penalty/views/hr_attendance_views.xml
- **Mục đích**: Định nghĩa views (Tree, Form, Search)
- **Nội dung chính**:
  - Tree view với `decoration-danger="is_late"` (hiểu đỏ khi đi muộn)
  - Form view hiển thị is_late, late_minutes
  - Search filters lọc theo "Đi muộn" / "Không muộn"

---

### 2. hr_salary_custom

#### hr_salary_custom/__manifest__.py
- **Mục đích**: Khai báo module
- **Nội dung chính**:
  - depends: ['hr', 'hr_attendance', 'hr_contract', 'hr_attendance_penalty']
  - data: ['bang_luong_views.xml', 'config_settings_views.xml']

#### hr_salary_custom/models/bang_luong.py
- **Mục đích**: Model phiếu lương tháng
- **Nội dung chính**:
  - Fields: employee_id, month, line_ids, state, tong_cong, tong_tru, thuc_lanh
  - Method: `action_generate_lines()` - tự động sinh dòng lương
  - Method: `_get_luong_co_ban()` - lấy lương từ hợp đồng
  - Method: `_calculate_phat_lines()` - tính phạt đi muộn
  - Methods: action_confirm(), action_cancel(), action_draft()
  - Computed fields tính lương thực nhận

#### hr_salary_custom/models/bang_luong_line.py
- **Mục đích**: Model chi tiết phiếu lương
- **Nội dung chính**:
  - Fields: name, amount, type (cong/tru), description, sequence
  - One2many relation về bang_luong

#### hr_salary_custom/models/config_settings.py
- **Mục đích**: Cấu hình tính lương
- **Nội dung chính**:
  - Inherits res.config.settings
  - Fields: standard_check_in_time, penalty_per_minute, default_wage, v.v.
  - get_values() & set_values() để đọc/ghi config

#### hr_salary_custom/views/bang_luong_views.xml
- **Mục đích**: Views cho bang.luong & bang.luong.line
- **Nội dung chính**:
  - Tree view danh sách phiếu lương
  - Form view chi tiết với header buttons (Tính lương, Xác nhận, etc.)
  - Inline editable tree cho line_ids
  - Display lương thực nhận (thuc_lanh)
  - Search/filter views

#### hr_salary_custom/views/config_settings_views.xml
- **Mục đích**: UI để cấu hình tính lương
- **Nội dung chính**:
  - Form view settings với các field config
  - Inherit base.res_config_settings_view_form

---

## 🔑 Key Features

### Module hr_attendance_penalty:
✅ Tự động xác định đi muộn  
✅ Tính số phút muộn (làm tròn lên)  
✅ Tree view với highlight màu đỏ  
✅ Cấu hình giờ chuẩn check-in  

### Module hr_salary_custom:
✅ Tạo phiếu lương tháng tự động  
✅ Tính lương cơ bản từ hợp đồng  
✅ Tính phạt đi muộn từ attendance  
✅ Chi tiết lương dạng editable  
✅ Computed fields: tong_cong, tong_tru, thuc_lanh  
✅ Workflow: draft → done → cancel  

---

## 📦 Dependencies

```
Odoo (base modules):
├── hr
├── hr_attendance
├── hr_contract
└── (ir - built-in)

Custom modules:
├── hr_attendance_penalty
└── hr_salary_custom
    └── depends on: hr_attendance_penalty
```

---

## 🚀 Deployment Steps

### 1. Copy modules
```bash
cp -r hr_attendance_penalty /path/to/odoo/addons/
cp -r hr_salary_custom /path/to/odoo/addons/
```

### 2. Install via Odoo UI
- Login as Administrator
- **Ứng dụng > Cập nhật danh sách modules**
- Search & install "HR Attendance Penalty"
- Search & install "HR Salary Custom"

### 3. Configure
- **Cài đặt > Tính lương tự động**
- Fill in: standard_check_in_time, penalty_per_minute, etc.

### 4. Use
- **Nhân sự > Chấm công** - xem danh sách đi muộn
- **Nhân sự > Phiếu lương** - tạo & tính lương

---

## 📊 Data Flow

```
User tạo Attendance (Check-in)
         ↓
hr.attendance.create() triggered
         ↓
hr_attendance_penalty.hr_attendance._compute_late_check_in()
         ↓
is_late & late_minutes được tính toán
         ↓
Record stored với is_late=True/False, late_minutes=N
         ↓
───────────────────────────────────────────
         ↓
User tạo bang.luong & nhấn "Tính lương"
         ↓
bang_luong.action_generate_lines() called
         ↓
Lấy lương cơ bản từ contract
         ↓
Tính tổng late_minutes từ hr.attendance
         ↓
Tính phạt = late_minutes × penalty_per_minute
         ↓
Tạo dòng lương (bang.luong.line) 
         ↓
Computed fields cập nhật: tong_cong, tong_tru, thuc_lanh
         ↓
User xác nhận → state='done'
```

---

## 🔧 Customization Points

| Điểm mở rộng | File | Method |
|-------------|------|--------|
| Thay đổi logic tính đi muộn | hr_attendance.py | `_compute_late_check_in()` |
| Thêm logic phạt về sớm | bang_luong.py | `_calculate_phat_lines()` |
| Thêm lương thưởng | bang_luong.py | `action_generate_lines()` |
| Thay đổi giờ chuẩn | config_settings.py | Fields |
| Mở rộng views | views/*.xml | XPath inherit |

---

## 📚 Tài liệu Liên quan

- **HƯỚNG_DẪN_SỬ_DỤNG.md**: Hướng dẫn cho end-user (Tiếng Việt)
- **API_DOCUMENTATION.md**: Tài liệu đầy đủ cho developer
- **README.md** (mỗi module): Giới thiệu nhanh
- **CHANGELOG.md**: Lịch sử phân phối

---

## ⚠️ Cảnh báo & Lưu ý

1. **Dependencies order**: Cài hr_attendance_penalty trước hr_salary_custom
2. **Data consistency**: Khi thay đổi config (giờ chuẩn, mức phạt), không tính lại attendance cũ
3. **Contract required**: Nên có hợp đồng cho mỗi nhân viên, nếu không dùng lương mặc định
4. **Month format**: Luôn dùng format YYYY-MM (VD: 2024-01, không phải 01/2024)
5. **Permissions**: Cần quyền HR Manager để thấy phiếu lương

---

**Phiên bản**: 1.0  
**Cập nhật**: 2024  
**Hỗ trợ**: Odoo 15, 16+  
**Ngôn ngữ**: Tiếng Việt (Vietnamese)
