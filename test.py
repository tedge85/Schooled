import unittest
import requests

from classes import Admin, Teacher, Student, Lesson, Security

API_URL = "http://127.0.0.1:5000"

class Tests(unittest.TestCase):
    user = Admin(login_email="admin@school.co.uk", password="strongpassword")                
    email = "test@school.co.uk"
          
    def test_assign_new_student_to_teacher(self):
        self.assertTrue(self.user.assign_new_student_to_teacher(self.email, 999, 3))


unittest.main()