{
    'name': 'HR Salary Custom',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'author': 'Your Company',
    'depends': ['hr', 'hr_attendance', 'hr_contract', 'hr_attendance_penalty'],
    'data': [
        'views/bang_luong_views.xml',
        'views/config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
