# HƯỚNG DẪN SỬ DỤNG CHI TIẾT - Modules Chấm Công & Tính Lương

## 📋 Nội dung

1. [Quy trình cài đặt](#cài-đặt)
2. [Cấu hình ban đầu](#cấu-hình)
3. [Quy trình tính lương](#quy-trình-tính-lương)
4. [Các tình huống thực tế](#tình-huống-thực-tế)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 Cài đặt

### Bước 1: Chuẩn bị
- Odoo 15 hoặc 16 đã được cài đặt với modules: `hr`, `hr_attendance`, `hr_contract`
- Thư mục `addons/` có thể ghi

### Bước 2: Sao chép modules
```bash
cp -r hr_attendance_penalty /path/to/odoo/addons/
cp -r hr_salary_custom /path/to/odoo/addons/
```

### Bước 3: Cài đặt trong Odoo
**Cách 1 (Giao diện)**:
1. Đăng nhập vào Odoo với tài khoản Administrator
2. **Ứng dụng > Cập nhật danh sách modules**
3. Tìm: "HR Attendance Penalty" → **Cài đặt**
4. Tìm: "HR Salary Custom" → **Cài đặt**

**Cách 2 (Command line)**:
```bash
./odoo-bin -d <database> -u hr_attendance_penalty,hr_salary_custom --stop-after-init
```

### Bước 4: Kiểm tra
- Menu **Cài đặt** có tùy chọn **"Tính lương tự động"**
- Menu **Nhân sự** có tùy chọn **"Chấm công"** và **"Phiếu lương"**

---

## ⚙️ Cấu hình

### 1. Truy cập Settings

**Đường dẫn**: 
- Nhấn biểu tượng **người dùng** (góc phải trên) 
- **Settings** 
- Tìm **"Tính lương tự động"** 

### 2. Các thông số cấu hình

#### a. Giờ chuẩn check-in
```
Giờ chuẩn check-in: 08:30
```
- **Format**: HH:MM
- **Ý nghĩa**: Nếu nhân viên check-in sau giờ này, sẽ bị đánh dấu "Đi muộn"
- **Ví dụ**: 
  - Giờ: 08:30
  - Check-in lúc 08:45 → Đi muộn 15 phút
  - Check-in lúc 08:15 → Không muộn

#### b. Mức phạt đi muộn
```
Mức phạt đi muộn (VND/phút): 1000
```
- **Đơn vị**: VND/phút
- **Ý nghĩa**: Mỗi phút muộn bị phạt bao nhiêu tiền
- **Ví dụ**: 
  - 1000 VND/phút
  - Muộn 120 phút → Phạt: 120,000 VND

#### c. Phạt về sớm (tùy chọn)
```
Mức phạt về sớm (VND/phút): 500
```
- Tương tự như phạt đi muộn
- Có thể để 0 nếu không muốn phạt về sớm

#### d. Lương cơ bản mặc định
```
Lương cơ bản mặc định (VND): 0
```
- **Sử dụng khi**: Nhân viên không có hợp đồng lao động
- **Độ ưu tiên**: 
  1. Lương từ hợp đồng (`hr.contract.wage`)
  2. Lương mặc định từ config
  3. Nếu cả hai là 0, phiếu lương sẽ không có lương cứng

### 3. Xác nhận lưu
- Sau khi điền tất cả, nhấn **Lưu**
- Cấu hình đã được lưu vào database

---

## 📊 Quy trình tính lương

### Quy trình tổng thể:
```
1. Nhân viên chấm công hàng ngày (Check-in/Check-out)
   ↓
2. Hệ thống tự động xác định "Đi muộn" (Module hr_attendance_penalty)
   ↓
3. Tạo phiếu lương cho nhân viên trong tháng
   ↓
4. Nhấn "Tính lương" → Hệ thống tự động:
   - Lấy lương cơ bản từ hợp đồng
   - Tính tổng phút muộn trong tháng
   - Tính phạt = phút muộn × mức phạt/phút
   - Ghi các khoản vào chi tiết lương
   ↓
5. Xác nhận phiếu lương → Chuyển thành "Hoàn tất"
```

### Chi tiết từng bước:

#### Bước 1: Chuẩn bị dữ liệu nhân viên
Đảm bảo mỗi nhân viên có:
- **Hợp đồng lao động** với mức lương `wage` được điền (nếu không sẽ dùng lương mặc định)
- Cách cấu hình:
  - **Nhân sự > Nhân viên** → Chọn nhân viên
  - Tab **"VIỆC LÀM"** → **"Hợp đồng lao động"**
  - Điền **"Lương"** (hoặc **"Wage"**)

#### Bước 2: Đăng ký chấm công hàng ngày
- **Nhân sự > Chấm công** 
- Check-in/Check-out của nhân viên được ghi nhận tự động (hoặc thêm thủ công)
- Hệ thống tự động tính `is_late` và `late_minutes`

**Xem chấm công đi muộn**:
- **Nhân sự > Chấm công** (Tree view)
- Các dòng có **"Đi muộn" = True** sẽ hiển thị màu **đỏ**
- Filter: **"Đi muộn"** để xem chỉ những người muộn

#### Bước 3: Tạo phiếu lương tháng
- **Nhân sự > Phiếu lương** (hoặc **Tính lương > Phiếu lương**)
- Nhấn **"Tạo"**
- Điền:
  - **Nhân viên**: Chọn nhân viên từ dropdown
  - **Tháng**: Nhập tháng (format: `YYYY-MM`, VD: `2024-01`)
  - State mặc định: "Bản nháp"
- Nhấn **"Lưu"**

#### Bước 4: Tính lương tự động
- Sau khi lưu phiếu lương ở trạng thái "Bản nháp"
- Nhấn nút **"Tính lương"** (màu xanh, ở header form)
- Hệ thống thực hiện:
  ```
  a. Xóa các dòng cũ (nếu có)
  b. Lấy lương cơ bản từ hợp đồng
  c. Tính tổng phút muộn trong tháng từ attendance
  d. Tính phạt (phút × rate)
  e. Thêm các khoản khác (nếu có)
  f. Tạo dòng lương tương ứng
  ```

#### Bước 5: Xem chi tiết lương
- Tab **"Chi tiết lương"**: Xem tất cả các khoản
  - Lương cứng (Cộng)
  - Phạt đi muộn (Trừ)
  - Các khoản khác
- Tab **"Ghi chú"**: Thêm ghi chú nếu cần
- Các field computed tự động cập nhật:
  - **Tổng cộng** = Tổng các khoản "Cộng"
  - **Tổng trừ** = Tổng các khoản "Trừ"
  - **Thực lãnh** = Tổng cộng - Tổng trừ

#### Bước 6: Sửa chi tiết lương (nếu cần)
- Có thể thêm/sửa/xóa các dòng chi tiết
- Bảng dòng lương ở mode "editable" → Có thể inline edit
- Ví dụ: Thêm các khoản thưởng, bổng cấp, etc.

#### Bước 7: Xác nhận phiếu lương
- Nhấn **"Xác nhận"** → State chuyển thành "Hoàn tất"
- Phiếu lương đã hoàn thành, sẵn sàng để xuất hoặc xử lý tiếp

---

## 📌 Tình huống thực tế

### Tình huống 1: Nhân viên đi muộn 1 ngày

**Dữ liệu ban đầu**:
- Nhân viên: Nguyễn Văn A
- Hợp đồng lương: 10,000,000 VND/tháng
- Giờ chuẩn check-in: 08:30
- Mức phạt: 1,000 VND/phút

**Sự kiện**:
- 15/01/2024: Check-in lúc 08:45 → Muộn 15 phút
- Phần còn lại tháng: Check-in đúng giờ

**Kết quả**:
```
Phiếu lương tháng 1/2024:
├─ Lương cứng:        10,000,000 VND (Cộng)
├─ Phạt đi muộn:      -15,000 VND     (Trừ = 15 phút × 1,000)
├─ Tổng cộng:         10,000,000 VND
├─ Tổng trừ:          15,000 VND
└─ Thực lãnh:         9,985,000 VND
```

### Tình huống 2: Nhân viên đi muộn nhiều ngày

**Dữ liệu ban đầu**:
- Nhân viên: Trần Thị B
- Hợp đồng lương: 8,000,000 VND/tháng
- Giờ chuẩn check-in: 08:30
- Mức phạt: 1,000 VND/phút

**Sự kiện**:
- 03/02: Check-in 08:40 → Muộn 10 phút
- 07/02: Check-in 08:50 → Muộn 20 phút
- 15/02: Check-in 09:10 → Muộn 40 phút
- 20/02: Check-in 08:35 → Muộn 5 phút
- Tổng: 60 + 20 + 40 + 5 = 75 phút muộn

**Kết quả**:
```
Phiếu lương tháng 2/2024:
├─ Lương cứng:        8,000,000 VND (Cộng)
├─ Phạt đi muộn:      -75,000 VND    (Trừ = 75 phút × 1,000)
├─ Tổng cộng:         8,000,000 VND
├─ Tổng trừ:          75,000 VND
└─ Thực lãnh:         7,925,000 VND
```

### Tình huống 3: Nhân viên không có hợp đồng

**Dữ liệu ban đầu**:
- Nhân viên: Lê Văn C (không có hợp đồng)
- Cấu hình lương mặc định: 5,000,000 VND

**Kết quả**:
```
Phiếu lương:
├─ Lương cơ bản (mặc định): 5,000,000 VND (Cộng)
├─ Phạt đi muộn:           -... VND        (Trừ)
└─ Thực lãnh:              ... VND
```

### Tình huống 4: Thêm các khoản thưởng/bổng cấp

**Sau khi tính lương tự động**, có thể:
1. Thêm dòng lương mới:
   - **Name**: "Thưởng hiệu suất"
   - **Type**: "Cộng"
   - **Amount**: 500,000

2. Các trường computed tự động cập nhật:
   - Tổng cộng: 10,000,000 + 500,000 = 10,500,000
   - Thực lãnh: 10,500,000 - 15,000 = 10,485,000

---

## 🆘 Troubleshooting

### Vấn đề 1: "Không thấy menu Phiếu lương"
**Nguyên nhân**: Module `hr_salary_custom` chưa được cài đặt
**Giải pháp**:
1. **Ứng dụng > Cập nhật danh sách modules**
2. Tìm "HR Salary Custom" → **Cài đặt**
3. Refresh trang (F5)

### Vấn đề 2: Khi nhấn "Tính lương", không có dòng nào được tạo
**Nguyên nhân**:
- Nhân viên không có hợp đồng lương
- Cấu hình lương mặc định = 0

**Giải pháp**:
1. **Cài đặt > Tính lương tự động**
2. Điền **"Lương cơ bản mặc định"** > 0
3. Hoặc thêm hợp đồng cho nhân viên

### Vấn đề 3: "Đi muộn" không được tính toán
**Nguyên nhân**:
- Module `hr_attendance_penalty` chưa được cài đặt
- Hoặc nhân viên chấm công trước khi cài module

**Giải pháp**:
1. Cài đặt module `hr_attendance_penalty`
2. Thêm lại records attendance hoặc cập nhật from admin panel
3. Run: `SELECT * FROM hr_attendance WHERE employee_id = X;` để xem dữ liệu

### Vấn đề 4: Phạt đi muộn tính sai
**Nguyên nhân**:
- Giờ chuẩn không được đặt đúng
- Attendance record của nhân viên chưa được tính `is_late`

**Giải pháp**:
1. Kiểm tra **Cài đặt > Tính lương tự động** → **"Giờ chuẩn check-in"**
2. Kiểm tra **Nhân sự > Chấm công** → Xem field `is_late` và `late_minutes`
3. Nếu cần, có thể:
   - Xóa attendance record
   - Tạo lại với thông tin chính xác
   - Hệ thống sẽ tự động tính lại `is_late`

### Vấn đề 5: Không thể sửa phiếu lương sau khi xác nhận
**Giải pháp**:
- Nhấn **"Quay lại bản nháp"** → Chuyển state về "Bản nháp"
- Lúc này có thể sửa được
- Sau sửa: **"Xác nhận"** lại

---

## 📞 Liên hệ & Hỗ trợ

Nếu gặp sự cố:
1. Kiểm tra file logs trong folder `logs/` của Odoo
2. Cách bật debug mode:
   ```bash
   ./odoo-bin -d <database> --log-level=debug
   ```
3. Liên hệ nhóm phát triển để báo cáo lỗi

---

**Phiên bản**: 1.0  
**Cập nhật**: 2024  
**Hỗ trợ**: Odoo 15, 16+
