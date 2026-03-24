# Hướng Dẫn Tính Lương Theo Ngày (Daily Rate)

## Thay Đổi Từ Lương Theo Giờ → Lương Theo Ngày

### ❌ CỚI (Tính theo giờ - Hourly)
```
Lương thực = Tổng giờ làm × (Lương hợp đồng / 160 giờ/tháng)
```

### ✅ MỚI (Tính theo ngày - Daily Rate)
```
Lương thực = Số ngày làm × (Lương hợp đồng / 26 ngày làm việc)
```

---

## Công Thức Chi Tiết

### Bước 1: Tính Daily Rate (Lương Theo Ngày)
```
Daily Rate = Lương Hợp Đồng (Toàn Bộ Tháng) / 26 ngày
```

**Ví Dụ:**
```
Lương hợp đồng = 10,000,000 VND/tháng
Daily Rate = 10,000,000 / 26 = 384,615.38 VND/ngày
```

### Bước 2: Đếm Số Ngày Làm Việc Thực Tế
- Lấy từ **hr.attendance records** trong tháng
- Đếm **số ngày distinct** có check_in
- Không tính giờ làm, chỉ tính số ngày

**Ví Dụ:**
```
Tháng 03/2026 có attendance records:
- 24/03: check_in 09:30 → tính 1 ngày
- 25/03: check_in 08:45 → tính 1 ngày
Tổng = 2 ngày → actual_working_days = 2
```

### Bước 3: Tính Lương Thực
```
Lương Thực = Daily Rate × Số Ngày Làm Việc
```

**Ví Dụ:**
```
Lương Thực = 384,615.38 × 2 = 769,230.76 VND
```

### Bước 4: Tính Các Khoản Trừ (Insurance, Penalties)

#### Insurance (Bảo hiểm)
```
BHXH = Lương Thực × 8%
BHYT = Lương Thực × 1.5%
BHTN = Lương Thực × 1%
Tổng Bảo Hiểm = BHXH + BHYT + BHTN = Lương Thực × 10.5%
```

**Ví Dụ:**
```
Lương Thực = 769,230.76
Tổng Bảo Hiểm = 769,230.76 × 10.5% = 80,769.23 VND
  - BHXH (8%): 61,538.46
  - BHYT (1.5%): 11,538.46
  - BHTN (1%): 7,692.31
```

#### Late Penalty (Phạt đi muộn)
```
Phạt Đi Muộn = Tổng Phút Muộn × Mức Phạt (VND/phút)
```

**Ví Dụ:**
```
Tổng phút muộn trong tháng = 45 phút
Mức phạt = 1,000 VND/phút
Phạt Đi Muộn = 45 × 1,000 = 45,000 VND
```

---

## Thực Lãnh Cuối Cùng

```
Thực Lãnh = Lương Thực - Tổng Bảo Hiểm - Phạt Đi Muộn
```

**Ví Dụ Đầy Đủ:**
```
Lương Hợp Đồng = 10,000,000 VND/tháng
Daily Rate = 10,000,000 / 26 = 384,615.38 VND/ngày
Số Ngày Làm = 2 ngày
Lương Thực = 384,615.38 × 2 = 769,230.76 VND

Trừ Bảo Hiểm = 769,230.76 × 10.5% = 80,769.23 VND
Trừ Phạt Muộn = 45,000 VND

Thực Lãnh = 769,230.76 - 80,769.23 - 45,000 = 643,461.53 VND
```

---

## Trong Phiếu Lương (Chi Tiết Dòng)

| Dòng | Nội Dung | Loại | Số Tiền |
|------|----------|------|---------|
| 1 | Lương cơ bản (2 ngày × 384,615.38) | Cộng (+) | 769,230.76 |
| 2 | Phạt đi muộn | Trừ (-) | 45,000.00 |
| 3 | Bảo hiểm (BHXH, BHYT, BHTN) | Trừ (-) | 80,769.23 |
| | **Tổng Cộng** | | **769,230.76** |
| | **Tổng Trừ** | | **125,769.23** |
| | **THỰC LÃNH** | | **643,461.53** |

---

## Lợi Ích Của Daily Rate

1. ✅ **Công Bằng Hơn**: Tính theo ngày làm việc thực tế, không bị ảnh hưởng bởi giờ làm
2. ✅ **Dễ Hiểu**: Nhân viên dễ hiểu: "10 triệu chia 26 ngày = X/ngày"
3. ✅ **Theo Chuẩn**: Phù hợp với luật lao động Việt Nam (tính theo ngày công)
4. ✅ **Tự Động**: Hệ thống tự động đếm ngày làm từ hr.attendance

---

## Cài Đặt Cấu Hình (Nếu Cần Thay Đổi)

**Settings > HR Salary Custom:**

| Tham Số | Giá Trị Mặc Định | Mô Tả |
|---------|-----------------|-------|
| `default_wage` | 10,000,000 | Lương mặc định (nếu hợp đồng không có) |
| `penalty_per_minute` | 1,000 | Mức phạt/phút đi muộn (VND) |
| `insurance_bhxh_rate` | 8% | Tỷ lệ BHXH |
| `insurance_bhyt_rate` | 1.5% | Tỷ lệ BHYT |
| `insurance_bhtn_rate` | 1% | Tỷ lệ BHTN |

---

## Câu Hỏi Thường Gặp

### Q: Nếu nhân viên không có attendance record trong tháng thì sao?
**A:** Hệ thống sẽ **không tạo dòng lương cơ bản** vì không biết số ngày làm. Bạn cần phải thêm attendance record trước.

### Q: Nếu nhân viên làm 26 ngày (toàn bộ tháng)?
**A:** Lương = 10,000,000 VND (toàn bộ lương hợp đồng)
- Daily Rate = 10,000,000 / 26 = 384,615.38
- Lương Thực = 384,615.38 × 26 = 10,000,000

### Q: Nếu làm thêm ngày 27, 28, 29, 30, 31?
**A:** Tất cả được tính với **cùng daily rate**:
- Lương = 384,615.38 × 31 = 11,923,076.78 VND
- Không có "+500k" cho mỗi ngày, mà là tính theo daily rate như bình thường

### Q: Insurance tính trên cái gì?
**A:** **Trên lương thực** (sau khi tính theo số ngày làm), **không phải lương hợp đồng toàn bộ**:
```
Bảo Hiểm = (Lương Hợp Đồng / 26 × Số Ngày Làm) × 10.5%
```

---

## Cach Deploy Thay Đổi

```bash
cd /home/hung/16-06-N11
python odoo-bin -d <database_name> -u hr_salary_custom --stop-after-init
```

Sau đó tạo **new payslip** để áp dụng logic mới.

