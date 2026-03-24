# API Reference - hr_salary_advanced

## Models Reference

### hr.attendance (Extended)

**New Fields**:
```python
is_late: Boolean          # True if check_in > standard_time (computed, stored)
late_minutes: Integer    # Minutes late (computed, stored)
```

**Computed Methods**:
```python
_compute_is_late()      # Auto-compute is_late based on check_in and config
_compute_late_minutes() # Auto-compute late_minutes
```

**Example**:
```python
# Create attendance
att = env['hr.attendance'].create({
    'employee_id': 5,
    'check_in': datetime(2024, 1, 15, 8, 45),  # 08:45 (15 min late)
    'check_out': datetime(2024, 1, 15, 17, 30),
})

# Access computed fields
print(att.is_late)       # True
print(att.late_minutes)  # 15
```

---

### hr.shift.register

**Model Name**: `hr.shift.register`

**Fields**:
```python
employee_id: Many2one('hr.employee')     # Required
month: Char                              # Format: YYYY-MM
shift_ids: One2many('hr.shift.detail')   # Shift details
state: Selection                         # draft/submitted/approved
total_days: Integer                      # Computed, excludes 'off'
```

**Methods**:
```python
def action_submit()     # Change state to submitted
def action_approve()    # Change state to approved, auto-create attendance
def action_draft()      # Back to draft
def _create_attendance_records()  # Create hr.attendance from shifts
```

**Example**:
```python
# Create shift register
register = env['hr.shift.register'].create({
    'employee_id': 5,
    'month': '2024-01',
})

# Add shift details
env['hr.shift.detail'].create({
    'register_id': register.id,
    'date': date(2024, 1, 1),
    'shift_type': 'full',
})

# Submit
register.action_submit()

# Approve (auto-creates attendance)
register.action_approve()

# Check total days
print(register.total_days)  # 20 (if 20 non-'off' days)
```

---

### hr.shift.detail

**Model Name**: `hr.shift.detail`

**Fields**:
```python
register_id: Many2one('hr.shift.register')  # Required
date: Date                                  # Required
shift_type: Selection                       # morning/afternoon/full/off
employee_id: Many2one (related)             # From register
month: Char (related)                       # From register
```

**Shift Types**:
- `morning`: 08:30-12:00
- `afternoon`: 13:00-17:30
- `full`: 08:30-17:30
- `off`: Day off (no attendance created)

---

### bang.luong (Payslip)

**Model Name**: `bang.luong`

**Key Fields - Inputs**:
```python
employee_id: Many2one('hr.employee')    # Required
month: Char                             # Format: YYYY-MM, Required
state: Selection                        # draft/done/cancel
line_ids: One2many('bang.luong.line')  # Detail line items
```

**Computed Fields - Outputs** (all store=True):
```python
basic_salary: Float                # From contract or config
standard_days: Integer            # Working days standard (default: 26)
actual_days: Integer              # Actual working days (computed from attendance)
overtime_days: Float              # = actual_days - standard_days
salary_by_days: Float             # (basic_salary / standard_days) * actual_days
overtime_bonus: Float             # = overtime_days * rate (500k default)
total_insurance: Float            # basic_salary * (8% + 1.5% + 1%)
late_penalty: Float               # = total_late_minutes * 10000/min
total_deductions: Float           # = total_insurance + late_penalty
net_salary: Float                 # = salary_by_days + overtime_bonus - total_deductions
```

**Methods**:
```python
def action_generate_lines()  # Auto-generate line_ids from calculations
def action_confirm()         # Finalize payslip, generate lines
def action_draft()           # Back to draft
def action_cancel()          # Cancel
def create_payslip(employee_id, month)  # Static: create & calculate for employee
```

**Example**:
```python
# Create payslip
payslip = env['bang.luong'].create({
    'employee_id': 5,
    'month': '2024-01',
})

# Auto-calculate
payslip.action_generate_lines()

# Access calculations
print(f"Salary: {payslip.salary_by_days}")
print(f"Insurance: {payslip.total_insurance}")
print(f"Net: {payslip.net_salary}")

# Confirm
payslip.action_confirm()

# Alternative: Helper method
payslip = env['bang.luong'].create_payslip(employee_id=5, month='2024-01')
```

**Salary Calculation Formula**:
```python
If actual_days <= standard_days (26):
    salary_by_days = (basic_salary / standard_days) * actual_days
    overtime_bonus = 0

If actual_days > standard_days:
    salary_by_days = basic_salary  # Full month
    overtime_bonus = (actual_days - standard_days) * 500000

total_insurance = basic_salary * 0.105  # 8% + 1.5% + 1%

late_penalty = total_late_minutes * 10000  # Configurable

net_salary = salary_by_days + overtime_bonus - total_insurance - late_penalty
```

---

### bang.luong.line

**Model Name**: `bang.luong.line`

**Fields**:
```python
bang_luong_id: Many2one('bang.luong')  # Parent payslip
sequence: Integer                      # Display order
name: Char                            # Line description
amount: Float                         # Amount (always positive)
type: Selection                       # 'cong' (add) or 'tru' (subtract)
description: Text                    # Details/formula
```

**Example**:
```python
# Auto-created by action_generate_lines(), example:
{
    'bang_luong_id': payslip.id,
    'sequence': 10,
    'name': 'Lương Cơ Bản (20 ngày × 384,615)',
    'amount': 7692308,
    'type': 'cong',
    'description': '(10,000,000 / 26) × 20',
}
```

---

### res.config.settings (Extended)

**Configuration Fields**:
```python
standard_check_in_time = Char       # Default: '08:30'
basic_salary = Float                # Default: 10,000,000
standard_working_days = Integer     # Default: 26
overtime_rate = Float               # Default: 500,000
penalty_per_minute = Float          # Default: 10,000
insurance_bhxh_rate = Float         # Default: 0.08 (8%)
insurance_bhyt_rate = Float         # Default: 0.015 (1.5%)
insurance_bhtn_rate = Float         # Default: 0.01 (1%)
```

**Usage**:
```python
# Get config value
config = env['ir.config_parameter'].sudo()
standard_time = config.get_param('hr_salary_advanced.standard_check_in_time', '08:30')
rate_bhxh = float(config.get_param('hr_salary_advanced.insurance_bhxh_rate', '0.08'))

# Or via res.config.settings model (transient)
settings = env['res.config.settings'].create({})
print(settings.standard_check_in_time)
```

---

### payslip.wizard

**Model Name**: `payslip.wizard` (Transient)

**Fields**:
```python
month: Char                         # Required, YYYY-MM format
employee_ids: Many2many('hr.employee')  # Optional
note: Text                          # Optional
```

**Methods**:
```python
def action_create_payslips()  # Create payslips for employees + month
```

**Example**:
```python
# Use wizard
wizard = env['payslip.wizard'].create({
    'month': '2024-01',
    'employee_ids': [(6, 0, [5, 6, 7])],  # specific employees
    'note': 'Regular monthly payroll',
})
wizard.action_create_payslips()
# Returns success message

# Or programmatically
for employee in env['hr.employee'].search([('active', '=', True)]):
    env['bang.luong'].create_payslip(employee.id, '2024-01')
```

---

## Computed Field Dependencies

```
is_late
├── depends: check_in
└── triggers via: check_in time comparison

late_minutes
├── depends: check_in
└── needs: is_late = True

actual_days
├── depends: month, employee_id
└── source: distinct hr.attendance dates

overtime_days
├── depends: actual_days, standard_days
└── formula: max(0, actual_days - standard_days)

salary_by_days
├── depends: basic_salary, actual_days, standard_days
└── formula: (basic_salary / standard_days) * actual_days

overtime_bonus
├── depends: overtime_days, config(overtime_rate)
└── formula: overtime_days * rate

total_insurance
├── depends: basic_salary, config(insurance_rates)
└── formula: basic_salary * (8% + 1.5% + 1%)

late_penalty
├── depends: month, employee_id, config(penalty_rate)
└── source: sum(late_minutes) from ir.attendance

total_deductions
├── depends: total_insurance, late_penalty
└── formula: total_insurance + late_penalty

net_salary
├── depends: salary_by_days, overtime_bonus, total_deductions
└── formula: salary_by_days + overtime_bonus - total_deductions
```

---

## Security Rules

**Models**:
- `hr.attendance` -> read, write on own records
- `hr.shift.register` -> read, write own (before approval)
- `bang.luong` -> read only for own
- `bang.luong.line` -> read only

**Exceptions**:
- `hr.group_hr_manager`: Full access to all

**Record-Level Security**:
```xml
<!-- Employees see only own records -->
[('employee_id.user_id', '=', user.id)]

<!-- HR Managers see all -->
<!-- No domain restriction -->
```

---

## Common Tasks with Code Examples

### Task 1: Bulk Create Payslips for Month

```python
month = '2024-01'
employees = env['hr.employee'].search([('active', '=', True)])

for emp in employees:
    payslip = env['bang.luong'].create({
        'employee_id': emp.id,
        'month': month,
    })
    payslip.action_generate_lines()
    payslip.action_confirm()

message = f"Created {len(employees)} payslips for {month}"
```

### Task 2: Calculate Total Late Minutes for Employee in Month

```python
employee_id = 5
month = '2024-01'

year, month_num = map(int, month.split('-'))
start = datetime(year, month_num, 1)
end = datetime(year, month_num + 1, 1) - timedelta(days=1)

attendances = env['hr.attendance'].search([
    ('employee_id', '=', employee_id),
    ('check_in', '>=', f"{start.date()} 00:00:00"),
    ('check_in', '<=', f"{end.date()} 23:59:59"),
    ('is_late', '=', True),
])

total_late_minutes = sum(att.late_minutes for att in attendances)
total_penalty = total_late_minutes * 10000
print(f"Total late: {total_late_minutes} min = {total_penalty:,.0f} VND penalty")
```

### Task 3: Export Payslips to CSV

```python
month = '2024-01'
payslips = env['bang.luong'].search([('month', '=', month)])

import csv
with open(f'/tmp/payslips_{month}.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Employee', 'Days', 'Salary', 'Insurance', 'Penalty', 'Net'])
    
    for ps in payslips:
        writer.writerow([
            ps.employee_id.name,
            ps.actual_days,
            ps.salary_by_days,
            ps.total_insurance,
            ps.late_penalty,
            ps.net_salary,
        ])
```

### Task 4: Verify Employee's Payslip Calculations

```python
payslip = env['bang.luong'].browse(123)  # Or search

print("=== PAYSLIP VERIFICATION ===")
print(f"Employee: {payslip.employee_id.name}")
print(f"Month: {payslip.month}")
print()
print("INPUTS:")
print(f"  Basic Salary: {payslip.basic_salary:,.0f}")
print(f"  Standard Days: {payslip.standard_days}")
print(f"  Actual Days: {payslip.actual_days}")
print()
print("CALCULATIONS:")
print(f"  Daily Rate: {payslip.basic_salary / payslip.standard_days:,.2f}")
print(f"  Salary by Days: {payslip.salary_by_days:,.0f}")
print(f"  Overtime Days: {payslip.overtime_days:.1f}")
print(f"  Overtime Bonus: {payslip.overtime_bonus:,.0f}")
print(f"  Insurance (10.5%): {payslip.total_insurance:,.0f}")
print(f"  Late Penalty: {payslip.late_penalty:,.0f}")
print()
print(f"NET SALARY: {payslip.net_salary:,.0f}")
print()
print("LINES:")
for line in payslip.line_ids:
    symbol = "+" if line.type == 'cong' else "-"
    print(f"  {symbol} {line.name}: {line.amount:,.0f}")
```

---

## Debugging

### Enable Debug Logging

```python
# In payslip model methods
import logging
_logger = logging.getLogger(__name__)

_logger.info(f"Computing salary for {record.employee_id.name}")
_logger.warning(f"No attendance for {record.month}")
_logger.error(f"Contract wage not found for {employee_id}")
```

### Check Computed Field Cache

```python
payslip = env['bang.luong'].browse(123)

# Force recompute
payslip.invalidate_cache()
payslip._compute_salary_by_days()

# Or refresh from DB
payslip.env.clear()
payslip = env['bang.luong'].browse(123)
```

### Verify Attendance Data

```python
employee_id = 5
month = '2024-01'

attendances = env['hr.attendance'].search([
    ('employee_id', '=', employee_id),
    ('check_in', '>=', f'2024-01-01 00:00:00'),
])

for att in attendances:
    print(f"{att.check_in.date()}: {att.is_late=}, {att.late_minutes=} min")
```

---

## Performance Tips

1. **Use search filters**: Limit attendance queries by date range
   ```python
   # ❌ Bad: fetches all
   attendances = env['hr.attendance'].search([('employee_id', '=', emp_id)])
   
   # ✓ Good: filtered
   attendances = env['hr.attendance'].search([
       ('employee_id', '=', emp_id),
       ('check_in', '>=', start_date),
   ])
   ```

2. **Use stored computed fields**: Better for reporting
   - `ir.attendance.is_late` (store=True)
   - `bang.luong.actual_days` (store=True)
   - All are indexed for fast queries

3. **Batch operations**: Create multiple records at once
   ```python
   # Better than loop
   env['bang.luong'].create([
       {'employee_id': e.id, 'month': m} for e in employees
   ])
   ```

---

## Extending the Module

### Add Custom Deduction

In `bang_luong.py`:

```python
# Add field
custom_deduction = fields.Float(compute='_compute_custom')

# Add method
def _compute_custom(self):
    for record in self:
        record.custom_deduction = ...

# Add to line generation
def action_generate_lines(self):
    # ... existing code ...
    if record.custom_deduction > 0:
        lines_to_create.append({
            'bang_luong_id': record.id,
            'name': 'Custom Deduction',
            'amount': record.custom_deduction,
            'type': 'tru',
            'sequence': 65,
        })
```

### Add Custom Bonus

```python
# Similar to above
custom_bonus = fields.Float(compute='_compute_custom_bonus')

def _compute_custom_bonus(self):
    # ...

# In action_generate_lines():
if record.custom_bonus > 0:
    lines_to_create.append({
        'bang_luong_id': record.id,
        'name': 'Performance Bonus',
        'amount': record.custom_bonus,
        'type': 'cong',
        'sequence': 25,
    })
```

---

## Testing

### Unit Test Example

```python
from odoo.tests import TransactionCase

class TestPayslip(TransactionCase):
    def test_salary_calculation(self):
        """Test salary calculation for regular employee"""
        emp = self.env['hr.employee'].create({'name': 'Test'})
        payslip = self.env['bang.luong'].create({
            'employee_id': emp.id,
            'month': '2024-01',
        })
        
        # Mock: actual_days = 20
        payslip.actual_days = 20
        payslip._compute_salary_by_days()
        
        # Basic: 10M / 26 * 20 = 7.69M
        self.assertAlmostEqual(payslip.salary_by_days, 7692308, delta=1)
```

---

