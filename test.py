import unittest
import requests

from classes import Admin, Teacher, Student, Lesson, Security

API_URL = "http://127.0.0.1:5000"

class Tests(unittest.TestCase):
    user = Admin("admin@school.co.uk", "strongpassword", None, security=True)                
    email = "test@school.co.uk"
    secure_app = Security(1, security=True)
    user = Admin("admin@school.co.uk", "strongpassword", secure_app, security=True)   
    lesson = Lesson()

    def test_change_lesson_content(self):
        self.assertEqual(change_lesson_content())

unittest.main()