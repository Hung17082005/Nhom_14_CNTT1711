# CHANGELOG

Tất cả các thay đổi đáng chú ý sẽ được ghi lại tại đây.

## [1.0.0] - 2024

### Thêm mới

#### Module: hr_attendance_penalty
- Thêm fields vào `hr.attendance`: `is_late`, `late_minutes`
- Logic tự động tính `is_late` khi check-in
- Tree view chấm công với decoration-danger cho người đi muộn
- Search filters: "Đi muộn", "Không muộn"
- Config parameter: `standard_check_in_time` (giờ chuẩn check-in)

#### Module: hr_salary_custom
- Model mới: `bang.luong` (Phiếu lương)
- Model mới: `bang.luong.line` (Chi tiết phiếu lương)
- Method tự động sinh phiếu lương: `action_generate_lines()`
- Tính toán lương cơ bản từ hợp đồng
- Tính phạt đi muộn từ attendance records
- Form view với chi tiết lương dạng editable tree
- Config parameters:
  - `penalty_per_minute`: Mức phạt đi muộn
  - `default_wage`: Lương cấp bãi mặc định
  - `penalty_early_checkout`: Phạt về sớm (tùy chọn)

### Tài liệu
- README.md cho hr_attendance_penalty
- README.md cho hr_salary_custom
- HƯỚNG_DẪN_SỬ_DỤNG.md: Hướng dẫn chi tiết cho người dùng
- API_DOCUMENTATION.md: Tài liệu API cho lập trình viên
- CHANGELOG.md: Lịch sử thay đổi

### Cảnh báo

- Các computed fields (`is_late`, `late_minutes`) chỉ tính khi create/write
- Nên cài đặt `hr_attendance_penalty` trước `hr_salary_custom` để tránh lỗi dependency
- Phải cấu hình giờ chuẩn check-in trước khi dùng module

## Coming Soon (Phiên bản tương lai)

- [ ] Tích hợp với module sale (hoa hồng bán hàng)
- [ ] Tích hợp với module expense (khấu trừ chi phí)
- [ ] Report xuất phiếu lương PDF
- [ ] Scheduled action tính lương hằng tháng tự động
- [ ] Dashboard thống kê lương, phạt
- [ ] Tính năng phê duyệt phiếu lương (workflow)
- [ ] Log audit cho mỗi lần tính lương
- [ ] Hỗ trợ các khoản khoán khác: bảo hiểm, thuế, v.v.

## Known Issues

Hiện không có issue nào được biết đến

---

## Hướng dẫn Contributing

Nếu bạn muốn đóng góp:
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

Các module này phát triển cho Odoo 15/16. Vui lòng tuân theo license của Odoo.
