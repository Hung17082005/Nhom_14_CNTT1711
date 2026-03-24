# HR Salary Advanced Module - Odoo 15

## Overview

`hr_salary_advanced` is a comprehensive HR salary management module for Odoo 15 that provides:

- **Attendance Tracking**: Automatic late detection and late minutes calculation
- **Shift Registration**: Calendar-based shift registration with auto-attendance creation
- **Advanced Payroll**: Auto-calculated payslips with various deductions and bonuses
- **Insurance Deductions**: BHXH (8%), BHYT (1.5%), BHTN (1%) automatic calculation
- **Late Penalties**: Automatic penalty calculation based on late attendance
- **Bulk Payslip Creation**: Wizard to create payslips for all employees in a month

---

## Module Structure

```
hr_salary_advanced/
├── __manifest__.py           # Module manifest
├── __init__.py              # Main init
├── models/
│   ├── __init__.py
│   ├── hr_attendance.py     # Extend hr.attendance with is_late, late_minutes
│   ├── hr_shift_register.py # Shift registration model
│   ├── bang_luong.py        # Payslip model with auto-calculations
│   ├── bang_luong_line.py   # Payslip detail lines
│   └── config_settings.py   # Configuration/settings
├── views/
│   ├── __init__.py
│   ├── hr_attendance_views.xml       # Attendance tree/form/search views
│   ├── hr_shift_register_views.xml   # Shift registration & calendar views
│   ├── bang_luong_views.xml          # Payslip views
│   ├── config_settings_views.xml     # Settings view
│   └── menu_views.xml                # Menu definitions & actions
├── wizards/
│   ├── __init__.py
│   ├── payslip_wizard.py             # Bulk payslip creation wizard
│   └── payslip_wizard_views.xml      # Wizard view
└── security/
    ├── ir.model.access.csv  # Access control lists
    └── security.xml         # Record-level security rules
```

---

## Features

### 1. Attendance with Late Detection

**Models**: Extends `hr.attendance`

**New Fields**:
- `is_late` (Boolean): Auto-computed if check-in > 08:30
- `late_minutes` (Integer): Minutes late (e.g., if check-in at 08:45, late_minutes = 15)

**Views**:
- Tree view with red color for late attendance
- Filters for late/not-late employees

**Configuration**: 
- Standard check-in time: Settings > HR Salary Advanced > Chấm Công > Giờ Chuẩn Check-in (default: 08:30)

---

### 2. Shift Registration (Đăng Ký Ca Làm)

**Models**:
- `hr.shift.register`: Monthly shift registration per employee
- `hr.shift.detail`: Individual day shift details

**Features**:
- Register shifts for each day in a month
- Shift types: Morning (08:30-12:00), Afternoon (13:00-17:30), Full (08:30-17:30), Off
- States: Draft → Submitted → Approved
- Auto-create attendance records when approved

**Views**:
- List view with month, employee, total_days, state
- Form view with editable inline shifts table
- Calendar view for visual shift planning

**Workflow**:
1. Create shift register for employee + month
2. Fill in shift types for each day
3. Submit
4. HR Manager approves
5. Auto-create attendance records with default times

---

### 3. Salary Calculation by Working Days

**Model**: `bang.luong` (Payslip)

**Salary Calculation Logic**:

```
Standard working days = 26
If actual_days <= 26:
    salary = (basic_salary / 26) × actual_days

If actual_days > 26:
    salary = basic_salary + (overtime_days × 500,000)
    where overtime_days = actual_days - 26
```

**Example**:
- Basic salary: 10,000,000 VND/month
- Actual working days: 20
- Salary = (10,000,000 / 26) × 20 = 7,692,307.69 VND

**Overtime Example**:
- Actual working days: 28
- Overtime days: 28 - 26 = 2
- Salary = 10,000,000 + (2 × 500,000) = 11,000,000 VND

**Calculated Fields**:
- `salary_by_days`: Salary by actual working days
- `overtime_bonus`: Extra pay for days > 26
- `total_insurance`: BHXH + BHYT + BHTN
- `late_penalty`: Total late penalty for month
- `net_salary`: salary_by_days + overtime_bonus - total_insurance - late_penalty

---

### 4. Insurance Deductions (Bảo Hiểm)

**Rates** (configurable in Settings):
- BHXH (Social Insurance): 8%
- BHYT (Health Insurance): 1.5%
- BHTN (Unemployment Insurance): 1%
- **Total**: 10.5%

**Calculation**: Based on basic salary from employee's contract

**Example** (basic_salary = 10,000,000):
- BHXH: 10,000,000 × 8% = 800,000
- BHYT: 10,000,000 × 1.5% = 150,000
- BHTN: 10,000,000 × 1% = 100,000
- **Total**: 1,050,000 VND

---

### 5. Late Penalties (Phạt Đi Muộn)

**Penalty Rate** (configurable): 10,000 VND/minute (default)

**Calculation**: Sums all late_minutes for late attendance records in month

**Example**:
- Total late minutes: 45 minutes
- Penalty = 45 × 10,000 = 450,000 VND

---

### 6. Payslip (Phiếu Lương)

**Model**: `bang.luong`

**Fields**:
- `employee_id`: Employee
- `month`: YYYY-MM format
- `actual_days`: Calculated from attendance records
- `salary_by_days`: Auto-calculated
- `overtime_bonus`: Auto-calculated
- `total_insurance`: Auto-calculated
- `late_penalty`: Auto-calculated
- `net_salary`: Final take-home pay
- `line_ids`: Detail line items (one2many)

**Auto-Generated Lines** (when "Tính Lương" button clicked):
1. Lương Cơ Bản (salary_by_days) - Cộng
2. Thưởng Công Vượt (overtime_bonus) - Cộng (if > 0)
3. Bảo Hiểm (total_insurance) - Trừ
4. Phạt Đi Muộn (late_penalty) - Trừ (if > 0)

**Payslip States**:
- Draft: Initial state, can edit and recalculate
- Done: Confirmed, locked
- Cancel: Cancelled

**Payslip Form**:
- Summary tab: Color-coded summary of salary components
- Salary Details tab: Breakdown of all calculations
- Line Details tab: Individual line items with descriptions
- Notes tab: Free text notes

---

### 7. Bulk Payslip Creation Wizard

**Access**: Menu > Bảng Lương > Tạo Phiếu Lương

**Inputs**:
- Month (YYYY-MM)
- Employee selection (optional - leaves empty = all active employees)
- Note (optional)

**Action**: Creates payslips for selected employees with auto-calculated lines

---

### 8. Security & Permissions

**Access Control Levels**:

**Employees (base.group_user)**:
- Read: Own attendance, shift registers, payslips
- Write: Own shift registers (before approval)
- Create: Own shift registers
- No delete

**HR Manager (hr.group_hr_manager)**:
- Full access: Read, Write, Create, Delete on all records

**Record-Level Rules**:
- Employees: Can only see own records (via `employee_id.user_id == current_user`)
- HR Manager: No restrictions

---

## Installation & Setup

### 1. Install Module

```bash
cd /home/hung/16-06-N11
python odoo-bin -d <database> -u hr_salary_advanced --stop-after-init
```

### 2. Configure Settings

**Menu**: Settings > HR Salary Advanced > Cài Đặt

**Configure**:
- Standard check-in time: 08:30 (default)
- Basic salary: 10,000,000 (default)
- Standard working days: 26 (default)
- Overtime rate: 500,000 VND/day (default)
- Late penalty: 10,000 VND/minute (default)
- Insurance rates: BHXH 8%, BHYT 1.5%, BHTN 1% (defaults)

### 3. Add Employees

Ensure employees have:
- Contract with wage amount
- User account (for permission checking)

### 4. Start Using

**Workflow**:
1. **Shift Registration** (Optional):
   - Menu > Đăng Ký Ca > Danh Sách Đăng Ký
   - Create shift register for employee + month
   - Fill in shifts for each day
   - Submit and approve
   - Auto-create attendance

2. **Manual Attendance** (or auto from shifts):
   - Menu > Chấm Công > Danh Sách Chấm Công
   - Employees check in/out
   - System auto-calculates is_late, late_minutes

3. **Create Payslips**:
   - Menu > Bảng Lương > Tạo Phiếu Lương (wizard)
   - OR: Menu > Bảng Lương > Phiếu Lương > Create
   - Click "🔄 Tính Lương" to generate lines
   - Click "✓ Xác Nhận" to finalize
   - View in "💰 Tóm Tắt" tab

---

## Usage Examples

### Example 1: Regular Month (No Overtime)

**Setup**:
- Employee: John Doe
- Basic salary: 10,000,000
- Month: 2024-01
- Attendance: 20 days on time, 1 day late by 30 minutes

**Calculation**:
- Salary by days: (10,000,000 / 26) × 20 = 7,692,307.69
- Overtime bonus: 0 (20 ≤ 26)
- Insurance: 10,000,000 × 10.5% = 1,050,000
- Late penalty: 30 × 10,000 = 300,000
- **Net salary**: 7,692,307.69 - 1,050,000 - 300,000 = **6,342,307.69**

### Example 2: Overtime Month

**Setup**:
- Basic salary: 10,000,000
- Month: 2024-02
- Attendance: 28 days, all on time

**Calculation**:
- Actual days: 28
- Overtime days: 28 - 26 = 2
- Salary by days: 10,000,000 (full month)
- Overtime bonus: 2 × 500,000 = 1,000,000
- Insurance: 10,000,000 × 10.5% = 1,050,000
- Late penalty: 0
- **Net salary**: 10,000,000 + 1,000,000 - 1,050,000 = **9,950,000**

---

## Customization

### Change Insurance Rates

Settings > HR Salary Advanced > Cài Đặt > Bảo Hiểm Nhân Viên

Example: Change BHXH to 10%
- insurance_bhxh_rate = 0.10

### Change Late Penalty Rate

Settings > HR Salary Advanced > Cài Đặt > Phạt & Thưởng

Example: Change to 15,000 VND/minute
- penalty_per_minute = 15,000

### Change Overtime Bonus Rate

Settings > HR Salary Advanced > Cài Đặt > Phạt & Thưởng

Example: Change to 600,000 VND/day
- overtime_rate = 600,000

---

## Troubleshooting

### Q: Payslip shows 0 salary

**A**: Check:
1. Employee has contract with wage amount
2. Attendance records exist for the month
3. No is_invalid_time flag on attendance

### Q: Late minutes not calculating

**A**: Check:
1. Attendance check_in time is set correctly
2. is_late field is computed (wait for calculation)
3. Standard check-in time in settings matches expected time

### Q: Insurance not showing in payslip lines

**A**:
1. Click "🔄 Tính Lương" button to re-generate lines
2. Verify basic salary > 0
3. Check insurance rates are not 0 in settings

### Q: Employees can't see their own payslips

**A**:
1. Verify employee has user account linked
2. Check security rules in Security > security.xml
3. Verify employee.user_id field matches current user

---

## Database Integration Notes

**Extends**:
- `hr.attendance`: Adds is_late, late_minutes computed fields

**Related Models**:
- `hr.employee`: For employee info
- `hr.contract`: For wage information
- `res.config.settings`: For system parameters

**Key Computed Fields** (store=True):
- `hr.attendance.is_late`
- `hr.attendance.late_minutes`
- `bang.luong.actual_days`
- `bang.luong.overtime_days`
- `bang.luong.salary_by_days`
- `bang.luong.overtime_bonus`
- `bang.luong.total_insurance`
- `bang.luong.late_penalty`
- `bang.luong.net_salary`

All computed fields are stored in database for performance and auditing.

---

## File Manifest

| File | Purpose |
|------|---------|
| `__manifest__.py` | Module metadata, dependencies, data files |
| `models/hr_attendance.py` | Late detection logic |
| `models/hr_shift_register.py` | Shift registration models |
| `models/bang_luong.py` | Payslip calculation engine |
| `models/bang_luong_line.py` | Payslip detail lines |
| `models/config_settings.py` | Configuration parameters |
| `wizards/payslip_wizard.py` | Bulk payslip creation |
| `views/hr_attendance_views.xml` | Attendance UI |
| `views/hr_shift_register_views.xml` | Shift registration & calendar UI |
| `views/bang_luong_views.xml` | Payslip UI |
| `views/config_settings_views.xml` | Settings UI |
| `views/menu_views.xml` | Menus and actions |
| `wizards/payslip_wizard_views.xml` | Wizard UI |
| `security/ir.model.access.csv` | Access control |
| `security/security.xml` | Record-level security |

---

## API Methods

### HR Attendance

```python
# Create attendance
att = env['hr.attendance'].create({
    'employee_id': employee.id,
    'check_in': datetime.now(),
    'check_out': datetime.now() + timedelta(hours=8),
})
# is_late, late_minutes auto-computed
```

### Payslip

```python
# Create payslip
payslip = env['bang.luong'].create({
    'employee_id': employee.id,
    'month': '2024-01',
})

# Generate line items
payslip.action_generate_lines()

# Confirm payslip
payslip.action_confirm()

# Helper: create and calculate for employee in month
payslip = env['bang.luong'].create_payslip(employee_id, '2024-01')
```

### Shift Registration

```python
# Create shift register
register = env['hr.shift.register'].create({
    'employee_id': employee.id,
    'month': '2024-01',
})

# Add shifts
env['hr.shift.detail'].create({
    'register_id': register.id,
    'date': date(2024, 1, 1),
    'shift_type': 'full',
})

# Approve (auto-creates attendance)
register.action_approve()
```

---

## Version Info

- **Module Version**: 15.0.1.0.0
- **Odoo Version**: 15.0
- **Python**: 3.6+
- **Dependencies**: base, hr, hr_attendance, web

---

## License

LGPL-3

---

## Support

For issues or questions, refer to:
1. This documentation
2. Code comments in model files
3. View XML definitions for UI logic

