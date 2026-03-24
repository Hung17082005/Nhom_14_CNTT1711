# ✅ Installation Checklist

Use this checklist to ensure proper installation and configuration.

## Pre-Installation

- [ ] Odoo 15 is running
- [ ] Database exists (or will be created)
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Module files are in: `/home/hung/16-06-N11/addons/hr_salary_advanced/`
- [ ] Python syntax verified: `python -m py_compile models/*.py wizards/*.py`

## Installation

- [ ] Run install command:
  ```bash
  python odoo-bin -d <database_name> -u hr_salary_advanced --stop-after-init
  ```
- [ ] Check Odoo logs for errors (should see module loading)
- [ ] Restart Odoo service if needed
- [ ] Login to Odoo
- [ ] Module appears in: Apps > Filter: "Salary Advanced" or search "hr_salary_advanced"

## Configuration

- [ ] Menu > Settings > HR Salary Advanced > Cài Đặt
  - [ ] Giờ Chuẩn Check-in: 08:30 ✓
  - [ ] Lương Cơ Bản: 10,000,000 ✓
  - [ ] Số Công Chuẩn: 26 ✓
  - [ ] Thưởng Công Vượt: 500,000 ✓
  - [ ] Phạt/Phút Muộn: 10,000 ✓
  - [ ] BHXH: 8 ✓
  - [ ] BHYT: 1.5 ✓
  - [ ] BHTN: 1 ✓
- [ ] Click **Save**

## Employee Preparation

For each employee in payroll:

- [ ] Employee record exists (HR > Employees)
- [ ] User account is linked to employee
- [ ] Employee status: Active
- [ ] Employee has active hr.contract
- [ ] Contract has wage amount (e.g., 10,000,000)
- [ ] Contract status: Active

## Menu Verification

- [ ] Menu > HR Salary Advanced appears
- [ ] Submenu: Chấm Công (with Danh Sách Chấm Công)
- [ ] Submenu: Đăng Ký Ca (with Danh Sách Đăng Ký)
- [ ] Submenu: Bảng Lương (with Phiếu Lương, Tạo Phiếu Lương)
- [ ] Submenu: Cài Đặt (with Cài Đặt)

## Basic Testing

### Test 1: Attendance

- [ ] Menu > HR Salary Advanced > Chấm Công > Create
- [ ] Fill in employee, check_in (08:45), check_out (17:30)
- [ ] Save
- [ ] Row appears in RED (is_late = True)
- [ ] late_minutes = 15 ✓

### Test 2: Shift Registration

- [ ] Menu > HR Salary Advanced > Đăng Ký Ca > Create
- [ ] Employee: Select
- [ ] Month: 2024-01
- [ ] Add shifts (4+ days)
- [ ] Click **Gửi**
- [ ] Click **Duyệt**
- [ ] Attendance records auto-created
- [ ] Check: Menu > Chấm Công > New records visible ✓

### Test 3: Payslip Creation

- [ ] Menu > HR Salary Advanced > Bảng Lương > Tạo Phiếu Lương
- [ ] Month: 2024-01
- [ ] Employee: Leave empty (all active)
- [ ] Click **Tạo Phiếu Lương**
- [ ] Success message shown ✓
- [ ] Number of payslips created = number of active employees

### Test 4: Payslip Verification

- [ ] Menu > HR Salary Advanced > Bảng Lương > Open created payslip
- [ ] Tab 💰 Chi Tiết Lương:
  - [ ] actual_days > 0
  - [ ] salary_by_days calculated
  - [ ] total_insurance > 0
  - [ ] net_salary = salary - insurance - penalty
- [ ] Tab 📊 Tóm Tắt:
  - [ ] Color-coded boxes visible
  - [ ] Green (income), Red (deductions), Blue (net)
- [ ] Tab 📝 Chi Tiết Dòng:
  - [ ] 3-4 lines visible (salary, bonus, insurance, penalty)
- [ ] Line descriptions show formula

### Test 5: Permissions

**Login as Employee (not HR Manager)**:
- [ ] Can see own attendance only
- [ ] Can see own payslips only
- [ ] Cannot create attendance
- [ ] Cannot edit payslips

**Login as HR Manager**:
- [ ] Can see all employees' records
- [ ] Can create/edit attendance
- [ ] Can approve shift registers
- [ ] Can create/edit payslips

## Data Validation

- [ ] No payslip shows 0 salary (if attendance exists)
- [ ] Insurance always > 0 when basic_salary > 0
- [ ] net_salary = salary + bonus - insurance - penalty (math correct)
- [ ] late_minutes correctly calculated (check_in - standard_time)
- [ ] Tree view summation working (sum row at bottom)

## Performance Checks

- [ ] Payslip form loads within 2 seconds
- [ ] Wizard responds within 1 second
- [ ] Tree view updates instantly after state change
- [ ] Calendar view displays shifts correctly
- [ ] Searches by employee/month return results quickly

## Security Checks

- [ ] Employees cannot see other employees' records
- [ ] Employees cannot delete any records
- [ ] HR Managers can see all records
- [ ] Record-level rules enforced (search with domain)

## Documentation Review

- [ ] README.md accessible and readable
- [ ] INSTALLATION.md contains all setup steps
- [ ] API_REFERENCE.md has code examples
- [ ] BUILD_SUMMARY.md shows what was built

## Backup & Recovery

- [ ] Database backed up before installation
- [ ] Backup location known: _____________
- [ ] Recovery procedure documented
- [ ] Test restore plan (optional)

## Troubleshooting

If any issue occurs:

1. Check logs:
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

2. Restart module:
   ```bash
   python odoo-bin -d <database> -u hr_salary_advanced --stop-after-init
   ```

3. Clear cache:
   ```bash
   python odoo-bin -d <database> --addons-path=addons --clear-cache -u all
   ```

4. Refer to documentation files (README.md, INSTALLATION.md)

5. Check model relationships (many2one, one2many links)

## Go Live Checklist

Only proceed to production after confirming all above:

- [ ] All installation steps completed
- [ ] All configuration done
- [ ] All tests passed
- [ ] Permissions verified
- [ ] Performance acceptable
- [ ] Team trained on usage
- [ ] Backup in place
- [ ] Documentation reviewed
- [ ] Help desk contacted (if applicable)

## Sign-Off

- [ ] Installation completed by: _______________
- [ ] Date: _______________
- [ ] Verified by: _______________
- [ ] Date: _______________

---

**Ready for Production**: ☐ YES  ☐ NO

Comments: _________________________________________________________________

