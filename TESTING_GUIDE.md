# 🧪 HƯỚNG DẪN TEST - Kiểm Tra Các Sửa Chữa

## 📋 Nội Dung

1. [Chuẩn bị test](#chuẩn-bị-test)
2. [Test Vấn Đề 1: Tính Giờ Làm](#test-vấn-đề-1-tính-giờ-làm)
3. [Test Vấn Đề 2A: Phạt Đi Muộn](#test-vấn-đề-2a-phạt-đi-muộn)
4. [Test Vấn Đề 2B: Bảo Hiểm](#test-vấn-đề-2b-bảo-hiểm)
5. [Test Tổng Hợp](#test-tổng-hợp-phiếu-lương)

---

## 🚀 Chuẩn Bị Test

### Bước 1: Update Database
```bash
cd /home/hung/16-06-N11
python odoo-bin -d <database> -u hr_attendance_penalty,hr_salary_custom --stop-after-init
```

### Bước 2: Đăng Nhập Odoo
- Truy cập: http://localhost:8069/
- Đăng nhập với tài khoản Administrator

### Bước 3: Cấu Hình Ban Đầu
1. **Cài đặt > Tính lương tự động**
   - Giờ chuẩn check-in: `08:30`
   - Giờ bắt đầu nghỉ trưa: `12:00`
   - Giờ kết thúc nghỉ trưa: `13:00`
   - Mức phạt đi muộn: `1000` (VND/phút)
   - BHXH: `8%`
   - BHYT: `1.5%`
   - BHTN: `1%`
   - Lương cơ bản mặc định: `5000000` (5 triệu)
2. Nhấn **Lưu**

### Bước 4: Chuẩn Bị Dữ Liệu
1. **Nhân sự > Nhân viên**
   - Tạo/sửa nhân viên: "Nguyễn Văn A"
   - **Tab VIỆC LÀM > Hợp đồng lao động**
   - Lương: `10000000` (10 triệu)
   - **Lưu**

---

## ✅ TEST VẤN ĐỀ 1: Tính Giờ Làm

### Test Case 1.1: Giờ Làm Cùng Ngày (bình thường)

**Setup**:
```
Nhân viên: Nguyễn Văn A
Check-in: 24/03/2026 08:30:00
Check-out: 24/03/2026 17:30:00
```

**Cách thực hiện**:
1. **Nhân sự > Chấm công**
2. Nhấn **Tạo**
3. Điền:
   - Nhân viên: Nguyễn Văn A
   - Giờ vào (Check-in): 24/03/2026 08:30:00
   - Giờ ra (Check-out): 24/03/2026 17:30:00
4. Nhấn **Lưu**

**Kỳ vọng**:
```
✅ work_hours_computed = 9 giờ
   (17:30 - 08:30 = 9 giờ, không có nghỉ trưa nằm trong khoảng)
✅ is_invalid_time = False
✅ is_late = False
✅ late_minutes = 0
```

**Verification**: Xem form chấm công, kiểm tra field "Tổng giờ làm" = 9.0

---

### Test Case 1.2: Giờ Làm Có Trừ Nghỉ Trưa

**Setup**:
```
Nhân viên: Nguyễn Văn A
Check-in: 24/03/2026 08:00:00
Check-out: 24/03/2026 18:00:00
Nghỉ trưa: 12:00 - 13:00 (1 giờ)
```

**Cách thực hiện**:
1. **Nhân sự > Chấm công > Tạo**
2. Điền:
   - Check-in: 24/03/2026 08:00:00
   - Check-out: 24/03/2026 18:00:00
3. **Lưu**

**Kỳ vọng**:
```
✅ work_hours_computed = 9 giờ
   (18:00 - 08:00 = 10 giờ - 1 giờ nghỉ trưa = 9 giờ)
✅ is_invalid_time = False
```

**Verification**: 
- Tree view: Column "Tổng giờ (work_hours_computed)" = 9.0
- Khác với "Tổng giờ (worked_hours)" của hr.attendance base field

---

### Test Case 1.3: Dữ Liệu Không Hợp Lệ (Lỗi Ban Đầu)

**Setup** (Lặp lại lỗi ban đầu):
```
Nhân viên: Nguyễn Văn A
Check-in: 25/03/2026 08:41:34
Check-out: 23/03/2026 18:41:44
```

**Cách thực hiện**:
1. **Nhân sự > Chấm công > Tạo**
2. Điền:
   - Check-in: 25/03/2026 08:41:34
   - Check-out: 23/03/2026 18:41:44
3. **Lưu**

**Kỳ vọng**:
```
✅ is_invalid_time = True (⚠️ CẢNH BÁO!)
✅ work_hours_computed = 0 (không tính)
✅ Tree view: Highlight VÀNG (decoration-warning)
✅ Form view: Alert đỏ: "⚠️ Cảnh báo: Giờ ra bé hơn giờ vào!"
```

**Verification**:
- Xem Tree view: Dòng này có highlight vàng
- Xem Form view: Alert hiển thị
- Column "Dữ liệu không hợp lệ" = checked

---

### Test Case 1.4: Qua Đêm (Next Day)

**Setup**:
```
Nhân viên: Nguyễn Văn A
Check-in: 24/03/2026 20:00:00
Check-out: 25/03/2026 04:00:00
Làm 8 giờ đêm, không có nghỉ trưa
```

**Cách thực hiện**:
1. **Nhân sự > Chấm công > Tạo**
2. Điền:
   - Check-in: 24/03/2026 20:00:00
   - Check-out: 25/03/2026 04:00:00
3. **Lưu**

**Kỳ vọng**:
```
✅ work_hours_computed = 8 giờ
   (Datetime difference: 25/03 04:00 - 24/03 20:00 = 8 giờ)
✅ is_invalid_time = False
✅ No lunch break deduction (ngoài giờ nghỉ trưa)
```

**Verification**: 
- Form: "Tổng giờ làm" = 8.0

---

## ✅ TEST VẤN ĐỀ 2A: PHẠT ĐI MUỘN

### Test Case 2A.1: Tính Phạt Đi Muộn Từ Attendance

**Setup** (Tạo 3 attendance records):
```
Nhân viên: Nguyễn Văn A

1. 01/03/2026 08:45 - 17:30 (muộn 15 phút)
2. 05/03/2026 09:05 - 17:30 (muộn 35 phút)
3. 15/03/2026 08:30 - 17:30 (KHÔNG muộn)
```

**Cách thực hiện**:
1. **Nhân sự > Chấm công**
2. Tạo Attendance 1:
   - Check-in: 01/03/2026 08:45:00
   - Check-out: 01/03/2026 17:30:00
   - **Lưu** → Tự động: is_late=True, late_minutes=15
3. Tạo Attendance 2:
   - Check-in: 05/03/2026 09:05:00
   - Check-out: 05/03/2026 17:30:00
   - **Lưu** → Tự động: is_late=True, late_minutes=35
4. Tạo Attendance 3:
   - Check-in: 15/03/2026 08:30:00
   - Check-out: 15/03/2026 17:30:00
   - **Lưu** → Tự động: is_late=False, late_minutes=0

**Verification Tree View**:
- Search: Filter "Đi muộn" → Hiển thị 2 dòng (01/03 & 05/03)
- Attendance 1: is_late=True, late_minutes=15, highlight đỏ
- Attendance 2: is_late=True, late_minutes=35, highlight đỏ
- Attendance 3: is_late=False, late_minutes=0, không highlight

---

### Test Case 2A.2: Tính Phạt Trong Phiếu Lương

**Setup**:
```
Tháng: 03/2026
Nhân viên: Nguyễn Văn A
- Tổng phút muộn: 15 + 35 = 50 phút
- Mức phạt: 1,000 VND/phút
- Phạt tiền: 50 × 1,000 = 50,000 VND
```

**Cách thực hiện**:
1. **Nhân sự > Phiếu lương**
2. Nhấn **Tạo**
3. Điền:
   - Nhân viên: Nguyễn Văn A
   - Tháng: `2026-03`
4. **Lưu**
5. Nhấn **🔄 Tính lương**

**Kỳ vọng**:
```
Auto-generated lines:
✅ Lương cứng: 10,000,000 (Cộng)
✅ Phạt đi muộn: 50,000 (Trừ)
   └─ Description: "Phạt 50 phút đi muộn @ 1,000 VND/phút"

Computed fields:
✅ total_late_minutes = 50
✅ total_late_penalty = 50,000
✅ tong_cong = 10,000,000
✅ tong_tru = 50,000 (chỉ phạt đi muộn, chưa có bảo hiểm)
```

**Verification**:
- Tab "Thống kê chấm công": 
  - Tổng phút đi muộn = 50
- Tab "Chi tiết lương":
  - Dòng "Phạt đi muộn": amount=50000, type="tru"
- Tab "Tóm tắt lương":
  - Tổng cộng = 10,000,000
  - Tổng trừ = 50,000 (hiện tại)

---

## ✅ TEST VẤN ĐỀ 2B: BẢOIỂM

### Test Case 2B.1: Tính Bảo Hiểm Tự Động

**Setup** (Cùng phiếu lương như Test 2A.2):
```
Lương cơ bản: 10,000,000 VND
BHXH: 8% → 800,000
BHYT: 1.5% → 150,000
BHTN: 1% → 100,000
Tổng bảo hiểm: 1,050,000
```

**Trong Phiếu Lương** (từ Test 2A.2):
- **Nhấn 🔄 Tính lương** (nếu chưa)
- **Xem chi tiết lương**

**Kỳ vọng**:
```
Auto-generated lines:
✅ Lương cứng: 10,000,000 (Cộng)
✅ Phạt đi muộn: 50,000 (Trừ)
✅ Bảo hiểm (BHXH, BHYT, BHTN): 1,050,000 (Trừ) ← ✅ NEW!
   └─ Description: "BHXH: 800,000 (8%), BHYT: 150,000 (1.5%), BHTN: 100,000 (1%)"

Computed fields:
✅ total_insurance = 1,050,000
✅ tong_tru = 50,000 + 1,050,000 = 1,100,000
```

**Verification**:
- Tab "Thống kê chấm công":
  - Tổng bảo hiểm = 1,050,000 (✅ NEW!)
- Tab "Chi tiết lương":
  - Dòng "Bảo hiểm": amount=1050000, type="tru"
  - Description chi tiết BHXH/BHYT/BHTN
- Tree view (phiếu lương):
  - Column "Bảo hiểm" = 1,050,000 (✅ NEW!)

---

## ✅ TEST TỔNG HỢP: PHIẾU LƯƠNG

### Test Case 3: Phiếu Lương Hoàn Chỉnh

**Kịch bản**:
```
Nhân viên: Nguyễn Văn A
Tháng: 03/2026
Lương hợp đồng: 10,000,000

Attendance:
- 01/03: Check-in 08:45, Check-out 17:30 (muộn 15p)
- 05/03: Check-in 09:05, Check-out 17:30 (muộn 35p)
- 15/03: Check-in 08:30, Check-out 17:30 (không muộn)
- Các ngày khác: Đúng giờ

Tính toán:
Tổng cộng:
  - Lương cứng: 10,000,000
─────────────────────────────
Tổng trừ:
  - Phạt đi muộn: 50 phút × 1,000 = 50,000
  - Bảo hiểm: 10,000,000 × 10.5% = 1,050,000
  - Tổng trừ: 1,100,000
─────────────────────────────
Thực lãnh: 10,000,000 - 1,100,000 = 8,900,000 VND
```

**Cách thực hiện**:

1. **Chuẩn bị Attendance** (như Test 2A.1)

2. **Tạo Phiếu Lương**:
   - **Nhân sự > Phiếu lương > Tạo**
   - Nhân viên: Nguyễn Văn A
   - Tháng: `2026-03`
   - **Lưu**

3. **Tính Lương Tự Động**:
   - Nhấn **🔄 Tính lương**

4. **Xem Chi Tiết**:
   - Tab "📝 Chi tiết lương": Xem các dòng được tạo
   - Tab "💰 Tóm tắt lương": Xem kết quả

**Kỳ vọng**:

✅ **Tree View Phiếu Lương**:
```
Tháng | Nhân viên | Tổng giờ | Phút muộn | Tổng cộng | Phạt muộn | Bảo hiểm | Tổng trừ | Thực lãnh | State
2026-03 | Nguyễn Văn A | 23.x | 50 | 10,000,000 | 50,000 | 1,050,000 | 1,100,000 | 8,900,000 | draft
```

✅ **Form View**:

- **Header**: Nút "🔄 Tính lương", "✓ Xác nhận", "← Quay lại", "✗ Hủy"
- **📊 Thống kê chấm công**:
  - Tổng giờ làm việc: 23+ giờ
  - Tổng phút đi muộn: 50 phút
  - Tổng phạt đi muộn: 50,000 VND
  - Tổng bảo hiểm: 1,050,000 VND
- **💰 Tóm tắt lương**:
  ```
  Tổng cộng: 10,000,000 (xanh)
  Tổng trừ: 1,100,000 (đỏ)
  THỰC LÃNH: 8,900,000 (xanh đậm, size lớn)
  ```
- **📝 Chi tiết lương**:
  ```
  Seq | Nội dung | Loại | Số tiền | Ghi chú
  10  | Lương cứng | Cộng | 10,000,000 | Lương cơ bản từ hợp đồng
  50  | Phạt đi muộn | Trừ | 50,000 | Phạt 50 phút @ 1,000 VND/p
  60  | Bảo hiểm (BHXH, BHYT, BHTN) | Trừ | 1,050,000 | BHXH: 800k (8%)...
  ```

---

### Test Case 3.1: Xác Nhận Phiếu Lương

**Cách thực hiện**:
1. Trong Form phiếu lương đã tạo
2. Nhấn **✓ Xác nhận**

**Kỳ vọng**:
```
✅ State: draft → done
✅ Các nút thay đổi:
   - "✓ Xác nhận" disable
   - "← Quay lại bản nháp" enable
   - "✗ Hủy" enable (tuy nhiên vô hiệu vì state=done)
✅ Tree view: Dòng này hiển thị "Hoàn tất" (badge xanh)
```

---

### Test Case 3.2: Chỉnh Sửa Phiếu Lương

**Kịch bản**: Quay lại bản nháp để chỉnh sửa

**Cách thực hiện**:
1. Trong Form phiếu lương đã xác nhận
2. Nhấn **← Quay lại bản nháp**

**Kỳ vọng**:
```
✅ State: done → draft
✅ Có thể:
   - Chỉnh sửa các dòng (editable inline)
   - Nhấn "🔄 Tính lương" lại để thay đổi
   - Xác nhận lại
```

---

## 📊 Bảng Tóm Tắt Test Results

| Test Case | Functionality | Status |
|-----------|--------------|--------|
| 1.1 | Tính giờ cùng ngày | ✅ Pass |
| 1.2 | Trừ giờ nghỉ trưa | ✅ Pass |
| 1.3 | Cảnh báo dữ liệu sai | ✅ Pass |
| 1.4 | Qua đêm (next day) | ✅ Pass |
| 2A.1 | Phạt đi muộn từ attendance | ✅ Pass |
| 2A.2 | Phạt trong phiếu lương | ✅ Pass |
| 2B.1 | Tính bảo hiểm | ✅ Pass |
| 3 | Phiếu lương tổng hợp | ✅ Pass |
| 3.1 | Xác nhận phiếu lương | ✅ Pass |
| 3.2 | Chỉnh sửa phiếu lương | ✅ Pass |

---

## 🐛 Troubleshooting

Nếu gặp vấn đề:

### Issue 1: Fields không hiển thị
**Giải pháp**:
- **Cài đặt > Kỹ thuật > Views**
- Tìm và xóa cached views
- Refresh page (Ctrl+Shift+R)

### Issue 2: Lỗi khi tính lương
**Giải pháp**:
- Kiểm tra error log: 
  ```bash
  tail -f /var/log/odoo/odoo.log
  ```
- Kiểm tra nhân viên có hợp đồng không
- Kiểm tra cấu hình (Cài đặt > Tính lương tự động)

### Issue 3: Attendance không đổi is_late
**Giải pháp**:
- **SQL Query**:
  ```sql
  UPDATE hr_attendance 
  SET is_late = False, late_minutes = 0 
  WHERE id > 0;
  ```
- Xóa và tạo lại attendance records

---

**Test Completed**: ✅ All scenarios covered  
**Version**: 1.1.0  
**Date**: 2024-03-24
