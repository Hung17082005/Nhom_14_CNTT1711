<img width="1919" height="1125" alt="image" src="https://github.com/user-attachments/assets/6a673c80-365b-4e68-8566-11bd3f2257e6" /><h1 align="center">
QUẢN LÝ CHẤM CÔNG VÀ TÍNH LƯƠNG
</h1>
<div align="center">
  <img src="README/logoDaiNam.png" alt="DaiNam University Logo" width="250">
  <img src="README/fitdnu_logo.png" alt="KHOA CÔNG NGHỆ THỐNG TIN" width="250">
  <img src="README/aiotlab_logo.png" alt="AIOT Lab DNU Logo" width="250">
</div>
<br>
<div align="center">

[![FIT DNU](https://img.shields.io/badge/-FIT%20DNU-28a745?style=for-the-badge)](https://fitdnu.net/)
[![DAINAM UNIVERSITY](https://img.shields.io/badge/-DAINAM%20UNIVERSITY-dc3545?style=for-the-badge)](https://dainam.edu.vn/vi)

</div>

<div align="center">

[![XML](https://img.shields.io/badge/XML-FF6600?style=for-the-badge&logo=codeforces&logoColor=white)](https://www.w3.org/XML/)
[![Odoo](https://img.shields.io/badge/Odoo-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

</div>

<hr>

<div align="center">

#  Poster
[Nhom14.pptx](https://github.com/user-attachments/files/26233961/Nhom14.pptx)


</div>

<hr>

<div align="center">

# Giới thiệu hệ thống

</div>

### Mô tả hệ thống
Hệ thống được xây dựng trên nền tảng **Odoo ERP** nhằm tối ưu hóa toàn diện quy trình quản trị nhân sự, chấm công và tự động hóa bảng lương cho tổ chức.

* **Tự động hóa Tính lương:** Kết xuất bảng lương chuẩn xác từ dữ liệu chấm công thực tế, giúp loại bỏ sai sót thủ công và đảm bảo quyền lợi cho người lao động.
* **Hệ thống Thông báo & Tương tác:** Tích hợp gửi thông báo kết quả phê duyệt và phiếu lương tự động qua Email, tối ưu hóa trải nghiệm nhân viên trong tổ chức.

### Công nghệ sử dụng
[![Odoo](https://img.shields.io/badge/Odoo-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Llama3.3](https://img.shields.io/badge/Llama_3.3-Groq_AI-orange?style=for-the-badge&logo=meta&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)


## 1. Cài đặt công cụ, môi trường và các thư viện cần thiết

### 1.1. Clone project.
git clone https://github.com/Hung17082005/Nhom_14_CNTT1711.git
git checkout 

### 1.2. cài đặt các thư viện cần thiết

Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
### 1.3. khởi tạo môi trường ảo.

`python3.10 -m venv ./venv`
Thay đổi trình thông dịch sang môi trường ảo và chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu

```
source venv/bin/activate
pip3 install -r requirements.txt
```

## 2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.

`docker-compose up -d`

## 3. Setup tham số chạy cho hệ thống

### 3.1. Khởi tạo odoo.conf

Tạo tệp **odoo.conf** có nội dung như sau:

```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431


## 4. Chạy hệ thống và cài đặt các ứng dụng cần thiết

Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

<hr>
## 6. GIAO DIỆN CÁC CHỨC NĂNG



Giao diện nhân sự
<img width="1919" height="1131" alt="image" src="https://github.com/user-attachments/assets/a78006f3-5491-4203-ad9b-215f2af834b7" />


Giao diện chấm công
<img width="1919" height="1134" alt="image" src="https://github.com/user-attachments/assets/522adb0b-dd6d-499b-8688-798bf576d38e" />

Giao diện tính lương
<img width="1919" height="1125" alt="image" src="https://github.com/user-attachments/assets/6f232caf-a7eb-49b1-8fc9-90f1df004dff" />

</hr>
