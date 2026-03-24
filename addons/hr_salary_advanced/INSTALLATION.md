# Installation & Quick Start Guide

## Step 1: Installation

```bash
# Navigate to workspace
cd /home/hung/16-06-N11

# Activate virtual environment
source venv/bin/activate

# Update the module
python odoo-bin -d <database_name> -u hr_salary_advanced --stop-after-init
```

Replace `<database_name>` with your actual Odoo database name.

## Step 2: Initial Configuration

### Access Settings

1. Open Odoo > Apps > Settings
2. Search for "HR Salary Advanced"
3. Click on Settings link OR go to Menu > HR Salary Advanced > Cài Đặt

### Configure Parameters

**⏰ Chấm Công (Attendance)**:
- Giờ Chuẩn Check-in: `08:30` (employee must check-in by this time)

**💰 Tính Lương (Salary Calculation)**:
- Lương Cơ Bản: `10,000,000` (default monthly salary)
- Số Công Chuẩn: `26` (standard working days/month)
- Thưởng Công Vượt: `500,000` (bonus per overtime day)

**⚠️ Phạt & Thưởng (Penalties)**:
- Phạt/Phút Muộn: `10,000` (penalty per minute late)

**🏥 Bảo Hiểm (Insurance Rates)**:
- BHXH: `8` (%)
- BHYT: `1.5` (%)
- BHTN: `1` (%)

Click **Save** after configuration.

## Step 3: Prepare Employee Data

Ensure each employee has:
1. **Valid hr.employee record** with:
   - Name
   - User account (for permission checking)
   
2. **Active hr.contract** with:
   - Wage amount (e.g., 10,000,000)
   - Employment date
   - Status: Active

## Step 4: Test Basic Workflow

### Test 1: Create Manual Attendance

1. Menu > HR Salary Advanced > Chấm Công > Danh Sách Chấm Công
2. Click **Create**
3. Select an employee
4. Set check-in: `2024-01-15 08:45` (15 minutes late)
5. Set check-out: `2024-01-15 17:30`
6. Click **Save**
7. **Verify**: 
   - `is_late` should be `True` (checked)
   - `late_minutes` should be `15`

**Tree view color check**: Row should be RED (danger decoration for late)

### Test 2: Create Shift Register

1. Menu > HR Salary Advanced > Đăng Ký Ca > Danh Sách Đăng Ký
2. Click **Create**
3. Employee: Select employee
4. Month: `2024-01`
5. In shifts table, add dates:
   - 01/01 → Full
   - 02/01 → Full
   - ... (add more days)
6. Click **Gửi** (Submit)
7. Click **Duyệt** (Approve) - should auto-create attendance records
8. Go to Attendance > should see new records created

### Test 3: Create Payslip

**Method A: Using Wizard (Recommended)**

1. Menu > HR Salary Advanced > Bảng Lương > Tạo Phiếu Lương
2. Month: `2024-01`
3. Employee: Select or leave empty for all
4. Click **Tạo Phiếu Lương**
5. Should show success message

**Method B: Manual Creation**

1. Menu > HR Salary Advanced > Bảng Lương > Phiếu Lương
2. Click **Create**
3. Employee: Select employee
4. Month: `2024-01`
5. Click **Tính Lương** (calculates all fields)
6. Click **Xác Nhận** (finalizes)
7. View tabs to verify calculations

### Test 4: Verify Payslip Calculation

**Open payslip** and check:

1. **💰 Chi Tiết Lương tab**:
   - Actual days: Should match attendance days
   - Salary by days: Should be calculated correctly
   - Total insurance: Should be present
   - Late penalty: Should reflect late minutes

2. **📊 Tóm Tắt tab**:
   - Green row: Salary components added (+)
   - Red rows: Deductions (-)
   - Blue row: THỰC LÃNH (net salary) = salary + bonus - deductions

3. **📝 Chi Tiết Dòng tab**:
   - Should have 4 lines (main salary, overtime if any, insurance, penalty if any)
   - Each with amount, type (cộng/trừ), description

## Step 5: Test Permissions

### Employee View

**Login as regular employee** (not HR manager):

1. Go to Menu > HR Salary Advanced > **Chấm Công**
2. Should see: ✅ Own attendance records only
3. Go to Menu > HR Salary Advanced > **Bảng Lương**
4. Should see: ✅ Own payslips only
5. Go to Menu > HR Salary Advanced > **Đăng Ký Ca**
6. Should see: ✅ Own shift registers only
7. Try to create → should fail (ReadOnly)
8. Try to delete → should fail (No permission)

### HR Manager View

**Login as HR manager**:

1. Go to Menu > HR Salary Advanced > **Chấm Công**
2. Should see: ✅ All employees' attendance
3. Go to Menu > HR Salary Advanced > **Bảng Lương**
4. Should see: ✅ All employees' payslips
5. Can Create/Edit/Delete

## Calculation Verification Example

**Input Data**:
- Employee: John Doe
- Contract wage: 10,000,000
- Month: 2024-01
- Attendance records: 20 days (all on time)
- Additional: 1 day late by 30 minutes

**Expected Calculation**:

```
1. Actual days = 20 (from attendance)
2. Overtime days = 20 - 26 = 0 (no overtime)
3. Salary by days = (10,000,000 / 26) × 20 = 7,692,307.69
4. Overtime bonus = 0
5. Insurance = 10,000,000 × (8% + 1.5% + 1%) = 1,050,000
6. Late penalty = 30 × 10,000 = 300,000
7. THỰC LÃNH = 7,692,307.69 - 1,050,000 - 300,000 = 6,342,307.69
```

**Verify in Payslip**:
- Tab: 💰 Chi Tiết Lương
  - actual_days: 20 ✓
  - overtime_days: 0 ✓
  - salary_by_days: 7,692,307.69 ✓  
  - overtime_bonus: 0 ✓
  - total_insurance: 1,050,000 ✓
  - late_penalty: 300,000 ✓
  - net_salary: 6,342,307.69 ✓

- Tab: 📊 Tóm Tắt
  - Row 1 (green): Lương Cơ Bản... = 7,692,307.69 ✓
  - Row 2 (red): Bảo Hiểm = 1,050,000 ✓
  - Row 3 (red): Phạt Đi Muộn = 300,000 ✓
  - Row 4 (blue): THỰC LÃNH = 6,342,307.69 ✓

- Tab: 📝 Chi Tiết Dòng
  - Line 1: Lương Cơ Bản (20 ngày × ...) | cộng | 7,692,307.69 ✓
  - Line 2: Bảo Hiểm | trừ | 1,050,000 ✓
  - Line 3: Phạt Đi Muộn | trừ | 300,000 ✓

## Troubleshooting

### Issue: Module not appearing in Apps

**Solution**:
```bash
# Clear cache and reinstall
python odoo-bin -d <database> --addons-path=addons --clear-cache -u all
```

### Issue: Computed fields showing 0

**Solution**:
1. Trigger manual recalculation: Click "🔄 Tính Lương" button
2. Restart Odoo service: `$ sudo systemctl restart odoo-server`
3. Check that attendance and contract records exist

### Issue: Permission denied when employee tries to submit shift register

**Expected behavior**: 
- Employee can only submit own shifts
- HR manager must approve shifts to create attendance

**Check**:
1. Is employee linked to user? (`employee_id.user_id` set?)
2. Does employee have `base.group_user` permission?

### Issue: Insurance calculation not showing

**Check**:
1. Basic salary > 0 (verify in contract or default_wage config)
2. Insurance rates not = 0 (check settings)
3. Click "🔄 Tính Lương" to regenerate lines

### Issue: Unpredictable salary in payslip

**Debug**:
1. Count attendance records: Menu > Chấm Công, filter by employee + month
2. Verify each check_in has valid datetime
3. Check for invalid_time flags (if using extended hr_attendance)
4. Manually verify: actual_days = count of distinct check_in dates

## Performance Notes

- Computed fields are **stored=True** (auto-indexed, good for reporting)
- Attendance queries filtered by date range (efficient)
- Bulk payslip creation indexed by employee_id + month
- Calendar view on shift_detail may be slower with large datasets

---

## Next Steps

After successful testing:

1. **Go Live**:
   - Use wizard to create payslips
   - Monitor for any edge cases
   
2. **Customize** (if needed):
   - Adjust rates in Settings
   - Modify penalty formulas in bang_luong.py
   - Add custom deductions in bang_luong.py
   
3. **Export Payslips**:
   - Tree view > Export to Excel/CSV
   - Use for payroll processing
   
4. **Maintain**:
   - Regular settings review
   - Monthly payslip auditing
   - Archive old payslips as needed

---

## Support & Issues

Refer to:
- **README.md** for complete feature documentation
- **Code comments** in models/ for logic explanations
- **XML files** in views/ for UI definition details

