import os
import requests
import json
import re
import hashlib
from cryptography.fernet import Fernet
from ratelimit import limits, sleep_and_retry

# Generate a key to encrypt API requests.
KEY = os.environ.get("ENCRYPTION_KEY")
FERNET = Fernet(KEY.encode())

class User():
    
    API_URL = "http://127.0.0.1:5000" 
       
    def __init__(self, login_email, password, security_object, security=False, admin=False, teacher=False, student=False):
                  
        self.login_email = login_email 
        self.password = password                                        
        self.secure_user = security_object
        self.admin = admin
        self.teacher = teacher
        self.student = student
        self.security = security                      

        if self.admin:
            self.user = "admin"
        elif self.teacher:
            self.user = "teacher"
        else:
            self.user = "student"
        
        if self.security:
            self.secure_user.check_limit()
        self.user_info = requests.get(f"{self.API_URL}/users/{self.user}s/{self.login_email}", verify=False, headers={"Content-Type": "application/json"}).json() 
        
        self.fname = self.user_info["fname"]
        self.lname = self.user_info["lname"]
        self.email = self.user_info["login_email"]

        if not self.admin:
            self.id =  self.user_info["id"]
            self.DOB = self.user_info["DOB"]                
            self.current_lesson_id = self.user_info["current_lesson_id"]
            self.subject = self.user_info["subject"]
        
            
    def view_user_profile(self):
        
        if self.admin:
            print(f'''\n****{self.user.capitalize()} PROFILE****\nName: {self.fname} {self.lname}\nEmail: {self.email}\n''')
        else:
            print(f'''\n****{self.user.capitalize()} PROFILE****\nName: {self.fname} {self.lname}\n{self.user} ID: {self.id}\nEmail: {self.email}\nDate of Birth: {self.DOB}\n''')
                                                   

class Admin(User):            

    def __init__(self, login_email, password, security_object, security=False, admin=True):
        super().__init__(login_email, password, security_object, security=False, admin=True)
        
        self.secure_user = security_object
        if self.security:
            self.secure_user.check_limit()
        self.admin_list = requests.get(f"{self.API_URL}/admin_list", verify=False, headers={"Content-Type": "application/json"}).json()        
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", verify=False, headers={"Content-Type": "application/json"}).json()
        self.student_list = requests.get(f"{self.API_URL}/student_list", verify=False, headers={"Content-Type": "application/json"}).json()

        self.security = security
        self.admin = admin                            
        
    def enrol_student(self):
        '''Registers a student user and adds them to student_list.json'''                    
        
        print("\n***Enrol student***")                
        
        new_student_email_num = self.return_new_student_email_number()
        
        login_email = f"student{new_student_email_num}@school.co.uk"
                        
        password = self.secure_user.sanitise_input(input("\nEnter a password for this user: "))
        
        # Hash the given password.        
        hashed_password = self.secure_user.hash_password(password) 

        student_id = self.return_new_student_id()
        fname = self.secure_user.sanitise_input(input("\nEnter new student's first name: "))
        lname = self.secure_user.sanitise_input(input("\nEnter new student's last name: "))
        dob = self.secure_user.sanitise_input(input("\nEnter new student's date of birth (DD.MM.YY): "))
        while True:
            try:
                subject = self.secure_user.sanitise_input(input('''\n**What subject will they be studying?**
                                 \nType 'E' for 'English': 
                                 \nType 'M' for 'Maths': 
                                 \nType 'S' for 'Science': 
                                 \nType 'C' for 'Computer Science': ''').lower())
                
                if subject == "e":
                    subject = "English"
                    break
                
                elif subject == "m":
                    subject = "Maths"
                    break

                elif subject == "s":
                    subject = "Science"
                    break
                
                elif subject == "c":
                    subject = "Computer Science"
                    break
                
            except KeyError:
                "\n!!Type a valid option!!\n"
                                   
        assigned_teacher_id = self.return_subject_teacher_id(subject) # Retrieve ID of teacher who teaches chosen subject        
        new_student_data = {
            "login_email": login_email,
            "hashed_password": hashed_password,
            "id": student_id,
            "fname": fname,
            "lname": lname,
            "DOB": dob,
            "subject": subject,
            "current_lesson_id": 1,
            "assigned_teacher_id": assigned_teacher_id
            }

        headers = {"Content-Type": "application/json"}  
        
        if self.security:
            self.secure_user.check_limit()
            
        response = requests.post(f"{self.API_URL}/users/admins/{login_email}", headers=headers, json=new_student_data)
        
        if response.status_code == 201:
            
            # Update assigned teacher record to include new student's id in 'assigned_students' value.
            self.assign_new_student_to_teacher(login_email, student_id, assigned_teacher_id)        

            # Re-load teacher and student list instance variables so that they are up-to-date.
            if self.security:
                self.secure_user.check_limit()
            self.student_list = requests.get(f"{self.API_URL}/student_list", headers={"Content-Type": "application/json"}).json()

            self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()            
            
            print("\n*********Student enrolled!***********\n")
            
            # Pass the json response (i.e. the new student dictionary) to 
            # view_user_info in order to display new user.            
            return self.view_users_info(response.json()) 
        
        return print("Oops! Something went wrong.")
                

    def assign_new_student_to_teacher(self, email, student_id, assigned_teacher_id):
        '''Updates assigned teacher record to include new student's id in 'assigned_students' value'''
        
        new_student_data = {
            "student_id": student_id,
            "assigned_teacher_id": assigned_teacher_id
            }

        # Call patch request to update teacher record.
        headers = {"Content-Type": "application/json"}
        
        if self.security:
            self.secure_user.check_limit()
        response = requests.patch(f"{self.API_URL}/users/teachers/{email}", headers=headers, json=new_student_data)
        
        if response.status_code == 200:
            return True
        
        else:
            return False
        

    def return_subject_teacher_id(self, subject):
        '''Retrieves teacher who teaches a given subject'''
        
        for teacher in self.teacher_list:
            if teacher["subject"] == subject:
                return teacher["id"]
            

    def return_new_student_email_number(self):
        '''Iterates through student list and returns the highest number 
        attached to an email and increments by 1.'''
        
        highest_email_num = 1
        for student in self.student_list:
            email_num = ''.join(filter(str.isdigit, student["login_email"]))
            if int(email_num) > highest_email_num:
                highest_email_num = int(email_num)
            
        return highest_email_num + 1
    

    def return_new_student_id(self):
        '''Iterates through student list and returns the highest number 
        attached to an email and increments by 1.'''
        
        highest_id_num = 1
        for student in self.student_list:            
            if int(student["id"]) > highest_id_num:
                highest_id_num = int(student["id"])
            
        return highest_id_num + 1        


    def delete_student(self):
        '''Removes given student from student_list.json'''
        
        print("***UNENROL STUDENT***")
        fname = self.secure_user.sanitise_input(input(f"\nEnter first name of student to unenrol: ").lower())
        lname = self.secure_user.sanitise_input(input(f"\nEnter last name of student to unenrol: ").lower())
        
        for student in self.student_list:
            
            if student["fname"].lower() == fname.lower() and student["lname"].lower() == lname.lower():
                email = student["login_email"]
                id_to_delete = student["id"]
                
                self.view_users_info(student) # Display student info to user.
                
                while True:
                    try:
                        decision = input("\n!!Are you sure you want to delete this student?!!\n\nSelect 'y' or 'n': ").lower()
                        if decision == "y":
                            if self.security:
                                self.secure_user.check_limit()
                            make_request = requests.delete(f"{self.API_URL}/users/admins/{email}", headers={"Content-Type": "application/json"})
                            make_request
            
                            self.remove_student_id_from_teacher_data(id_to_delete)                            
                            break
                        
                        elif decision == "n":
                            return
    
                    except KeyError:
                        "!!Choose 'y' or 'n'!!"  

                if self.security:
                    self.secure_user.check_limit()
                make_request_to_alter_list = requests.delete(f"{self.API_URL}/users/admins/{email}", headers={"Content-Type": "application/json"})
                make_request_to_alter_list 
                
                self.remove_student_id_from_teacher_data(id_to_delete) # Ensure assigned teacher's record removes deleted student ID from their record.

                # Re-load teacher and student list instance variables so that they are up-to-date.
                self.secure_user.check_limit()
                self.student_list = requests.get(f"{self.API_URL}/student_list", headers={"Content-Type": "application/json"}).json()
                
                self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()                                
                                
                return 
                                                    
        return print(f"{fname} {lname} has not yet been enrolled as a student.")
                               

    def remove_student_id_from_teacher_data(self, id_to_delete): 
        '''Makes a PATCH request to API to remove deleted student's id from 
        teacher['student_ids']'''                

        if self.security:
            self.secure_user.check_limit()
        headers = {"Content-Type": "application/json"}
        make_request = requests.patch(f"{self.API_URL}/users/students/assignedteacher/{id_to_delete}", headers=headers)
        make_request
                
        return print("\n***student deleted***\n")

    def search_for_user_by_name(self):
        '''searches for inputted name in given list.'''
        while True:
        
            try:
                print("\n***Search for Teacher or Student***\n")
                
                user_list = self.secure_user.sanitise_input(input("Type 't' to search for teacher or 's' to search for a student: ").lower())
                
                if user_list == "t":
                    user_list = self.teacher_list
                    user_type = "teacher"
                    break
                elif user_list == "s":
                    user_list = self.student_list
                    user_type = "student"
                    break                   
            except ValueError:
                "Choose a valid option."
                
        #if self.security:
        fname = self.secure_user.sanitise_input(input(f"\nEnter {user_type}'s first name: ")).lower()
            
        lname = self.secure_user.sanitise_input(input(f"\nEnter {user_type}'s last name: ")).lower()
                             
        for user in user_list:
            if user["fname"].lower() == fname and user["lname"].lower() == lname:
                return self.view_users_info(user)        

        return print(f"{fname} {lname} has not yet been registered as a {user_type}.")
    

    def search_for_user_by_id(self, id, user_list):
        '''Discrete method - searches for user by id in given list.'''
        for user in user_list:        
            if int(user["id"]) == id:
                return user
    

    def view_users_info(self, user):
        '''Displays teacher or student information.'''
        # If user is a teacher, find assigned students.
        if "teacher" in user["login_email"]:
            user_type = "Teacher"
            assigned_students_data = []  
            
            # Iterate through student_ids list, inputting each student id to retrieve their info.     
            i = 0
            while i < len(user["student_ids"]):
                student = self.search_for_user_by_id(user["student_ids"][i], self.student_list) 
                 
                assigned_students_data.append(student)
                 
                i += 1

            student_info = []
            for student in assigned_students_data:
                                      
                  info = f"\nID: {student['id']}\nFirst name: {student['fname']}\nLast name: {student['lname']}\nSubject: {student['subject']}\nEmail: {student['login_email']}\n"
                  student_info.append(info)
        
            student_info_str = "\n".join(student_info)
        
            return print(f"\n*****{user_type} info*****\n\nName: {user['fname']} {user['lname']}\nID: {user['id']}\nEmail: {user['login_email']}\nSubject: {user['subject']}\nActive lesson ID: {user['current_lesson_id']}\n\n***Assigned students***\n{student_info_str}\n")

        # If user is a student, find assigned teacher. 
        elif "student" in user["login_email"]:
            user_type = "Student"
            for teacher in self.teacher_list:
                if user["assigned_teacher_id"] == teacher["id"]:
                    assigned_teacher = teacher
                    break
    
            return print(f"\n*****{user_type} info*****\n\nName: {user['fname']} {user['lname']}\nID: {user['id']}\nEmail: {user['login_email']}\nSubject: {user['subject']}\nActive lesson ID: {user['current_lesson_id']}\n\n***Assigned teacher***\nName: {teacher['fname']} {teacher['lname']}\nSubject: {teacher['subject']}\nEmail: {teacher['login_email']}\n")

        else:
            return "This user has not yet been registered as a teacher or student."                          


    def view_students(self):
        '''Displays all students and corresponding info.'''

        # Re-load teacher and student list instance variables so that they are up-to-date.
        if self.security:
            self.secure_user.check_limit()
        self.student_list = requests.get(f"{self.API_URL}/student_list", headers={"Content-Type": "application/json"}).json()
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()            

        students_str = ""

        for student in self.student_list:
            students_str += f"\nName: {student['fname']} {student['lname']}\nID: {student['id']}\nEmail: {student['login_email']}\nSubject: {student['subject']}\nActive lesson ID: {student['current_lesson_id']}\n"                   
        
            for teacher in self.teacher_list:                
                if student["assigned_teacher_id"] == teacher["id"]:
                    assigned_teacher = teacher                                
                    students_str += f"\n***Assigned teacher***\nName: {assigned_teacher['fname']} {assigned_teacher['lname']}\nSubject: {assigned_teacher['subject']}\nEmail: {assigned_teacher['login_email']}\n\n----------------------------------------------------------------------------------"
        
        return print(f"\n*****Student info*****\n{students_str}")


class Teacher(User):        

    def __init__(self, login_email, password, security_object, security=False, teacher=True):
        super().__init__(login_email, password, security_object, security=False, teacher=True)                
        
        self.security = security        
        self.secure_user = security_object    
        self.teacher = teacher
        
        if self.security:
            self.secure_user.check_limit()
        self.assigned_student_names = [requests.get(f"{self.API_URL}/users/teachers/assignedstudent/{self.id}", verify=False, headers={"Content-Type": "application/json"}).json()]

    def view_assigned_students(self):                                
        '''Displays students assigned to given teacher'''    
        student_str = ""

        student_num = 1
        for student in self.assigned_student_names:
            for name in student:
                    
                student_str += f"\nStudent {student_num}: {name}\n"
                student_num +=1                                
            
        return print(f"\n*****Assigned students*****\n\n{student_str}")
        

class Student(User):        

    def __init__(self, login_email, password, security_object, security=False, student=True):
        super().__init__(login_email, password, security_object, security=False, student=True)
                
        self.security = security        
        self.secure_user = security_object    
        self.student = student
        
        if self.security:
            self.secure_user.check_limit()
        self.assigned_teacher = requests.get(f"{self.API_URL}/users/students/assignedteacher/{self.id}", verify=False, headers={"Content-Type": "application/json"}).json()
  
    def view_assigned_teacher(self):            
        '''Displays teacher information.'''
        fname = self.assigned_teacher["fname"]
        lname = self.assigned_teacher["lname"]
        email = self.assigned_teacher["login_email"]
        subject = self.assigned_teacher["subject"]
        return print(f"\n*****Assigned {subject} teacher*****\n\nName: {fname} {lname}\nEmail: {email}\n")                                                           
            

class Lesson(): ################################ Need to change security to True if switched on
    
    API_URL = "http://127.0.0.1:5000"
    
    def __init__(self, subject, security=False):
        
        self.subject = subject
        self.subject_to_search = subject.lower
        self.security = security
        
        self.secure_lesson = Security(1, security=self.security)

        if self.security:            
            self.secure_lesson.check_limit()
        self.subject_list_path = requests.get(f"{self.API_URL}/lessons/{self.subject}", verify=False, headers={"Content-Type": "application/json"})

        if self.subject_list_path.status_code != 404:
            lessons = self.subject_list_path.json()

        if self.security:
            self.secure_lesson.check_limit()
        self.lessons = requests.get(f"{self.API_URL}/lessons/{self.subject}", verify=False, 
                                             headers={"Content-Type": "application/json"}).json()               
        
        self.current_lesson_id = int(self.return_active_lesson_id())
        
        self.new_lesson_id = int(self.current_lesson_id) + 1
        
    def return_active_lesson_id(self):
        
        latest_lesson_id = 0
        
        for lesson in self.lessons:                        
            
            if str(lesson["subject"])== str(self.subject):                
                if int(lesson["lesson_id"]) > int(latest_lesson_id):
                    latest_lesson_id = int(lesson["lesson_id"])                                        
                            
        return latest_lesson_id
    

    def format_lesson_output(self, empty_list, lesson_list):
        '''Used in multiple methods to display lesson info appropriately.'''

        lesson_ID = lesson_list["lesson_id"]
        subject = lesson_list["subject"]
        title = lesson_list["title"]
        lesson_input = lesson_list["input"]
        
        q_num = 1
        question_str = ""
        for question in lesson_list["questions"]:            
            question_str += f"\n{q_num}) {question}\n"            
            q_num += 1
            continue
        
        
        a_num = 1
        answer_str = ""
        if lesson_list["answers"]:
            for answer in lesson_list["answers"]:
                answer_str += f"\n{a_num}) {answer}\n"            
                a_num += 1
                continue
        else:
            answer_str = "**No answers uploaded yet***" 
        
        if lesson_list["grade"] != "None":
            grade = lesson_list["grade"]
        else:
            grade = "***Grade not yet given***" 
    
        info = f"\nLesson ID: {lesson_ID}\nSubject: {subject}\nTitle: {title}\n\nInput: {lesson_input}\n\nQuestions: \n{question_str}\n\nAnswers: \n{answer_str}\n\nGrade: {grade}\n\n_______________________________________________________________________________"
    
        lesson_info_to_return = empty_list.append(info)
        
        return lesson_info_to_return
    
    #### Method called by admin only
    def view_all_lessons(self):
            
            lesson_info_to_return = []
    
            for lesson in self.lessons:
                self.format_lesson_output(lesson_info_to_return, lesson)
        
            info_str = "\n".join(lesson_info_to_return)

            return print(info_str)
        
        
    #### Methods called by teachers and students #########
    def view_all_my_lessons(self):                
        
        lesson_info_to_return = []
        print(self.subject)
        for lesson in self.lessons:
            if lesson["subject"].lower() == self.subject.lower():
                self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return print(info_str)
    

    def change_lesson_content(self, title=None, lesson_input=None, 
                              question_1=None, question_2=None, 
                              question_3=None, question_4=None, 
                              question_5=None, answer_1="", answer_2="",
                              answer_3="", answer_4="", answer_5="",
                              grade=None):
        
        '''Modifies lesson data.'''                
                
        new_lesson_data = {
            "lesson_id": (self.current_lesson_id),
            "subject": self.subject,
            "title": title,
            "input": lesson_input,
            "question_1": question_1,
            "question_2": question_2,
            "question_3": question_3,
            "question_4": question_4,
            "question_5": question_5,        
            "answer_1": answer_1,
            "answer_2": answer_2,
            "answer_3": answer_3,
            "answer_4": answer_4,
            "answer_5": answer_5,
            "grade": grade,
            "encrypted": self.security # Let server know if this data is encrypted.
        }
        
        headers = {"Content-Type": "application/json"}
        
        if self.security:
            self.secure_lesson.check_limit()
            data_string = json.dumps(new_lesson_data).encode("utf-8")
            new_lesson_data = FERNET.encrypt(data_string)
            response = requests.patch(f"{self.API_URL}/lessons/{self.subject}", headers=headers, data=new_lesson_data)
            
        else: 
            response = requests.patch(f"{self.API_URL}/lessons/{self.subject}", headers=headers, json=new_lesson_data)
        
        lesson_info_to_return = []

        # If patch was successful...
        if response.status_code == 200:                 
                        
            # Update self.lessons with data added via API to lesson_lis.json
            if self.security:
                self.secure_lesson.check_limit()
            self.lessons = requests.get(f"{self.API_URL}/lessons/{self.subject}",   
                                             headers={"Content-Type": "application/json"}).json()   

            self.format_lesson_output(lesson_info_to_return, self.retrieve_my_active_lesson())
                        
            info_str = "\n".join(lesson_info_to_return) 
            
            print("\n***Lesson Updated!***\n")
            return print(info_str)            
        
        else:
            return print(("Oops! Something went wrong."))

    def retrieve_my_active_lesson(self):
        for lesson in self.lessons:            
            
            if lesson["subject"].lower() == self.subject.lower() and int(self.current_lesson_id) == int(lesson["lesson_id"]):
                return lesson

    def view_my_active_lesson(self):            
        
        lesson_info_to_return = []

        self.format_lesson_output(lesson_info_to_return, self.retrieve_my_active_lesson())
            
        info_str = "\n".join(lesson_info_to_return) 
        
        ("\n***Active lesson***\n")        
        return print(info_str)        
        

    ##### Methods called only by teachers.
    def add_new_lesson(self):
        '''Adds a new lesson, automatically assigning lesson id.'''                
        
        print("\n***New lesson to upload***")
        title = self.secure_lesson.sanitise_input(input("\nEnter a lesson title: \n"))
        lesson_input = self.secure_lesson.sanitise_input(input("\nEnter teacher input: \n"))
        question_1 = self.secure_lesson.sanitise_input(input("Enter question 1: "))
        question_2 = self.secure_lesson.sanitise_input(input("Enter question 2: "))
        question_3 = self.secure_lesson.sanitise_input(input("Enter question 3: "))
        question_4 = self.secure_lesson.sanitise_input(input("Enter question 4: "))
        question_5 = self.secure_lesson.sanitise_input(input("Enter question 5: "))
        new_lesson_data = {
            "lesson_id": (self.new_lesson_id),
            "subject": self.subject,
            "title": title,
            "input": lesson_input,
            "question_1": question_1,
            "question_2": question_2,
            "question_3": question_3,
            "question_4": question_4,
            "question_5": question_5,        
            "answer_1": "",
            "answer_2": "",
            "answer_3": "",
            "answer_4": "",
            "answer_5": "",
            "grade": None,
        }
        headers = {"Content-Type": "application/json"}  
        
        if self.security:
            self.secure_lesson.check_limit()
        response = requests.post(f"{self.API_URL}/lessons/{self.subject}", headers=headers, json=new_lesson_data)
        if response.status_code == 201:
            
            lesson_info_to_return = []
            self.format_lesson_output(lesson_info_to_return, response.json())
        
            info_str = "\n".join(lesson_info_to_return)
            
            print("\n*********New lesson uploaded***********\n\n")
            return print(info_str) 
        
        return print("Oops! Something went wrong.")
    

    def update_lesson(self):
        '''Allows teacher to change the title, lesson input or questions.'''
        
        print("\n***Update your active lesson***\n")
        
        # Display current, active lesson.
        self.view_my_active_lesson()           
        
        while True:
            try:
                
                # Ask user which parts of the lesson they wish to change and default to None or "" so that the endpoint can
                # keep the values as they were if they detect these None or "" values.
                title_choice = self.secure_lesson.sanitise_input(input("Do you want to change the title? Type 'y' or 'n': ").lower())
                
                if title_choice == "y":
                    title = self.secure_lesson.sanitise_input(input("\nEnter a new lesson title: \n"))
                
                else:
                    title = None
                    
                input_choice = self.secure_lesson.sanitise_input(input("Do you want to change the teacher input? Type 'y' or 'n': ").lower())
                
                if input_choice == "y":
                    lesson_input = self.secure_lesson.sanitise_input(input("\nEnter new teacher input: \n"))
                else:
                    lesson_input = None                    
                
                question_choice_1 = self.secure_lesson.sanitise_input(input("Do you want to change question 1? Type 'y' or 'n': ").lower())
                
                if question_choice_1 == "y":                    
                    question_1 = self.secure_lesson.sanitise_input(input("\nEnter a new question 1: \n"))
                else:
                    question_1 = ""
                                
                question_choice_2 = self.secure_lesson.sanitise_input(input("Do you want to change question 2? Type 'y' or 'n': ").lower())

                if question_choice_2 == "y":                    
                    question_2 = self.secure_lesson.sanitise_input(input("\nEnter a new question 2: \n"))
                else:
                    question_2 = ""
                    
                question_choice_3 = self.secure_lesson.sanitise_input(input("Do you want to change question 3? Type 'y' or 'n': ").lower())
                    
                if question_choice_3 == "y":                    
                    question_3 = self.secure_lesson.sanitise_input(input("\nEnter a new question 3: \n"))
                else:
                    question_3 = ""
                    
                question_choice_4 = self.secure_lesson.sanitise_input(input("Do you want to change question 4? Type 'y' or 'n': ").lower())
                    
                if question_choice_4 == "y":                    
                    question_4 = self.secure_lesson.sanitise_input(input("\nEnter a new question 4: \n"))
                else:
                    question_4 = ""
                    
                question_choice_5 = self.secure_lesson.sanitise_input(input("Do you want to change question 5? Type 'y' or 'n': ").lower())
                    
                if question_choice_5 == "y":                    
                    question_5 = self.secure_lesson.sanitise_input(input("\nEnter a new question 5: \n"))
                else:
                    question_5 = ""
                                    
                break
            
            except KeyError:                
                print("\n!!Choose a valid option!!\n")                
                
        self.change_lesson_content(title=title, lesson_input=lesson_input, 
                              question_1=question_1, question_2=question_2, 
                              question_3=question_3, question_4=question_4, 
                              question_5=question_5)


    def assign_grade(self):
        '''Allows a teacher to modify the 'grade' data in an active lesson.'''
        
        print("\n***Update your active lesson grade***\n")
        
        # Display current, active lesson.
        self.view_my_active_lesson()     

        grade = self.secure_lesson.sanitise_input(input("\nEnter a new grade: \n"))
        
        self.change_lesson_content(grade=grade)
    

    # Methods called only by students.
    def add_answers(self):
        '''Modifies course content by changing answer values.'''
        
        print("\n***Update your active lesson answers***\n")                
        
        # Display current, active lesson.
        self.view_my_active_lesson()
        
        while True:
            try:                             
                
                answer_choice_1 = self.secure_lesson.sanitise_input(input("Do you want to answer question 1? Type 'y' or 'n': ").lower())
                
                if answer_choice_1 == "y":                    
                    answer_1 = self.secure_lesson.sanitise_input(input("\nEnter an answer for question 1: \n"))
                else:
                    answer_1 = ""                
                
                answer_choice_2 = self.secure_lesson.sanitise_input(input("Do you want to answer question 2? Type 'y' or 'n': ").lower())

                if answer_choice_2 == "y":                    
                    answer_2 = self.secure_lesson.sanitise_input(input("\nEnter an answer for question 2: \n"))
                else:
                    answer_2 = ""
                    
                answer_choice_3 = self.secure_lesson.sanitise_input(input("Do you want to answer question 3? Type 'y' or 'n': ").lower())
                    
                if answer_choice_3 == "y":                    
                    answer_3 = self.secure_lesson.sanitise_input(input("\nEnter an answer for question 3: \n"))
                else:
                    answer_3 = ""
                    
                answer_choice_4 = self.secure_lesson.sanitise_input(input("Do you want to answer question 4? Type 'y' or 'n': ").lower())
                    
                if answer_choice_4 == "y":                    
                    answer_4 = self.secure_lesson.sanitise_input(input("\nEnter an answer for question 4: \n"))
                else:
                    answer_4 = ""
                    
                answer_choice_5 = self.secure_lesson.sanitise_input(input("Do you want to answer question 5? Type 'y' or 'n': ").lower())
                    
                if answer_choice_5 == "y":                    
                    answer_5 = input("\nEnter an answer for question 5: \n")
                else:
                    answer_5 = ""
                                    
                break
            
            except KeyError:                
                print("\n!!Choose a valid option!!\n")                
                
        self.change_lesson_content(answer_1=answer_1, answer_2=answer_2, 
                              answer_3=answer_3, answer_4=answer_4, 
                              answer_5=answer_5)                        


class Security():
    
    def __init__(self, login_attempts, security=False):
                
        self.login_attempts = login_attempts        
        self.security = security

    CALLS = 4
    ############ Subtract to show attempts left    

    @sleep_and_retry
    @limits(calls=20, period=60)
    def check_limit(self):
        ''' Empty function just to check for calls to API 
        and lock some out if suspected DDOS attack'''        
        return                                                          # Code used from https://stackoverflow.com/questions/40748687/python-api-rate-limiting-how-to-limit-api-calls-globally
    

    @sleep_and_retry
    @limits(calls=3, period=60)
    def password_attempts_check(self):        
        '''Monitors login attempts, limiting to 4, with a 60 second lock-out'''
        if self.login_attempts == 4:
            return print(f"\n!!! One login attempt remaining until your account is locked !!!\n")            
            
        else:                        
            return
        

    def sanitise_input(self, input_str):
        '''Sanitises input so that it doesn't contain any scripts.'''
        sanitised_str = re.sub(r'<script\b[^>]*>(.*?)</script>', '', input_str, flags=re.IGNORECASE)    # Code used from https://www.educative.io/answers/how-to-sanitize-user-input-in-python
        
        # Sanitise input if security is activated.
        if self.security: 
            return sanitised_str
        else:
            return input_str

    
    def hash_password(self, password):
        '''Hashes a given password.'''

        return hashlib.sha256(password.encode()).hexdigest()
        
                              

    

    
   
    
    