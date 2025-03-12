import os
import requests
import json
import re
import hashlib
import pwinput
from cryptography.fernet import Fernet
from ratelimit import limits, sleep_and_retry

# Generate a key to encrypt API requests.
KEY = os.environ.get("ENCRYPTION_KEY")
FERNET = Fernet(KEY.encode())

class User():
    '''Factory class out of which all users are constructed.'''
    
    API_URL = "http://127.0.0.1:5000" 
       
    def __init__(self, login_email, password, security_object, security=False, 
                 admin=False, teacher=False, student=False):
                  
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
        self.user_info = requests.get(f"{self.API_URL}/users/{self.user}s/"
                                      f"{self.login_email}", verify=False, 
                                      headers={"Content-Type": 
                                               "application/json"}).json() 
        
        self.fname = self.user_info["fname"]
        self.lname = self.user_info["lname"]
        self.email = self.user_info["login_email"]

        if not self.admin:
            self.id =  self.user_info["id"]
            self.DOB = self.user_info["DOB"]                
            self.current_lesson_id = self.user_info["current_lesson_id"]
            self.subject = self.user_info["subject"]
        
            
    def view_user_profile(self):
        '''Displays user's own basic information.'''
        
        if self.admin:
            print(f"\n****{self.user.capitalize()} PROFILE****\nName:"
                  f" {self.fname} {self.lname}\nEmail: {self.email}\n")
        else:
            print(f"\n****{self.user.capitalize()} PROFILE****\nName:" 
                  f" {self.fname} {self.lname}\n{self.user} ID: {self.id}"
                  f"\nEmail: {self.email}\nDate of Birth: {self.DOB}\n")
                                                   

class Admin(User):            

    def __init__(self, login_email, password, security_object, security=False,
                 admin=True):
        super().__init__(login_email, password, security_object, 
                         security=False, admin=True)
        
        self.secure_user = security_object
        if self.security:
            self.secure_user.check_limit()
            
        self.admin_list = requests.get(f"{self.API_URL}/admin_list", 
                          verify=False, headers={"Content-Type": 
                          "application/json"}).json()        
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list",
                            verify=False, headers={"Content-Type": 
                            "application/json"}).json()
        self.student_list = requests.get(f"{self.API_URL}/student_list", 
                            verify=False, headers={"Content-Type": 
                            "application/json"}).json()

        self.security = security
        self.admin = admin                            
        
    def enrol_student(self):
        '''Registers a student user and adds them to student_list.json'''                    
        
        print("\n***Enrol student***")                
        
        new_student_email_num = self.return_new_student_email_number()
        
        login_email = f"student{new_student_email_num}@school.co.uk"
                        
        password = self.secure_user.sanitise_input(pwinput.pwinput("\nEnter" 
                                                " a password for this user: "))
        
        # Hash the given password.        
        hashed_password = self.secure_user.hash_password(password) 

        # Student id is automated, based on those already used.
        student_id = self.return_new_student_id()
        
        fname = self.secure_user.sanitise_input(input("\nEnter new student's" 
                                                            " first name: "))
        lname = self.secure_user.sanitise_input(input("\nEnter new student's" 
                                                            " last name: "))
        dob = self.secure_user.sanitise_input(input("\nEnter new student's"
                                                            " date of birth" 
                                                            " (DD.MM.YY): "))
        while True:
            try:
                subject = self.secure_user.sanitise_input(input("\n**What "
                                           " subject will they be studying?**"
                                                 " \nType 'E' for 'English': "
                                                   " \nType 'M' for 'Maths': "
                                                 " \nType 'S' for 'Science': "
                                        " \nType 'C' for 'Computer Science': ")
                                                                      .lower())
                
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
                
        # Retrieve ID of teacher who teaches chosen subject                                           
        assigned_teacher_id = self.return_subject_teacher_id(subject) 
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
        
        # If security activated, monitor and limit API calls, and encrypt
        # data to be sent to secure endpoint.
        if self.security:
            self.secure_user.check_limit() 
            data_string = json.dumps(new_student_data).encode("utf-8")
            new_student_data = FERNET.encrypt(data_string)
            response = requests.post(f"{self.API_URL}/users/secure/admins/"
                                         f"{login_email}", headers=headers, 
                                         data=new_student_data)
            
        else:
            
            response = requests.post(f"{self.API_URL}/users/admins/"
                                     f"{login_email}", headers=headers, 
                                     json=new_student_data)
        
        if response.status_code == 201:
            
            # Update assigned teacher record to include new student's id in 
            # 'assigned_students' value.
            self.assign_new_student_to_teacher(login_email, student_id, 
                                               assigned_teacher_id)        

            
            
            # If security activated, monitor and limit API calls.
            if self.security:
                self.secure_user.check_limit()
            
            # Re-load teacher and student list instance variables so that 
            # they are up-to-date.
            self.student_list = requests.get(f"{self.API_URL}/student_list", 
                                headers={"Content-Type": 
                                         "application/json"}).json()

            self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", 
                                headers={"Content-Type": 
                                         "application/json"}).json()            
            
            print("\n*********Student enrolled!***********\n")
            
            # Pass the json response (i.e. the new student dictionary) to 
            # view_user_info in order to display new user.            
            return self.view_users_info(response.json()) 
        
        return print("Oops! Something went wrong.")
                

    def assign_new_student_to_teacher(self, email, student_id, 
                                      assigned_teacher_id):
        '''Updates assigned teacher record to include new student's id in 
        'assigned_students' value'''
        
        new_student_data = {
            "student_id": student_id,
            "assigned_teacher_id": assigned_teacher_id
            }

        # Call patch request to update teacher record.
        headers = {"Content-Type": "application/json"}
        
        # If security activated, monitor and limit API calls, and encrypt
        # data to be sent to secure endpoint.
        if self.security:
                self.secure_user.check_limit()
                data_string = json.dumps(new_student_data).encode("utf-8")
                new_student_data = FERNET.encrypt(data_string)
                response = requests.patch(f"{self.API_URL}/users/secure/"
                           f"teachers/{email}", headers=headers, 
                           data=new_student_data)
            
        else:
            
            response = requests.patch(f"{self.API_URL}/users/teachers/{email}", 
                                      headers=headers, json=new_student_data)
        
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
        fname = self.secure_user.sanitise_input(input(f"\nEnter first name of "
                                                      "student to unenrol: ")
                                                       .lower())
        lname = self.secure_user.sanitise_input(input(f"\nEnter last name of "
                                                      f"student to unenrol: ")
                                                      .lower())
        
        for student in self.student_list:
            
            s_fname = student["fname"].lower()
            s_lname = student["lname"].lower()

            print(s_fname, s_lname)
            print(fname, lname)
            if s_fname == fname and s_lname:
                email = student["login_email"]
                id_to_delete = student["id"]
                
                self.view_users_info(student) # Display student info to user.
                
                # Confirm decision then send delete request if confirmed.
                while True:
                    try:
                        decision = input("\n!!Are you sure you want to delete"
                                         " this student?!!\n\nSelect 'y' or "
                                         "'n': ").lower()
                        if decision == "y":
                            if self.security:
                                self.secure_user.check_limit()
                                
                            make_request = requests.delete(f"{self.API_URL}"
                                           f"/users/admins/{email}", 
                                           headers={"Content-Type": 
                                                    "application/json"})
                            make_request
            
                            self.remove_student_id_from_teacher_data
                            (id_to_delete)                            
                            break
                        
                        elif decision == "n":
                            return
    
                    except KeyError:
                        "!!Choose 'y' or 'n'!!"  

                if self.security:
                    
                    self.secure_user.check_limit()
                
                make_request_to_alter_list = requests.delete(f"{self.API_URL}"
                                             f"/users/admins/{email}", 
                                             headers={"Content-Type": 
                                                      "application/json"})
                make_request_to_alter_list 
                
                # Ensure assigned teacher's record removes deleted student ID 
                # from their record.
                self.remove_student_id_from_teacher_data(id_to_delete) 

                # Re-load teacher and student list instance variables so that 
                # they are up-to-date.
                self.secure_user.check_limit()
                self.student_list = requests.get(f"{self.API_URL}"
                                    f"/student_list", headers={"Content-Type": 
                                                 "application/json"}).json()
                
                self.teacher_list = requests.get(f"{self.API_URL}"
                                    f"/teacher_list", headers={"Content-Type": 
                                    "application/json"}).json()                                
                                
                return 
                                                    
        return print(f"{fname} {lname} has not yet been enrolled as a student.")
                               

    def remove_student_id_from_teacher_data(self, id_to_delete): 
        '''Makes a PATCH request to API to remove deleted student's id from 
        teacher['student_ids']'''                

        if self.security:
            self.secure_user.check_limit()
            
        headers = {"Content-Type": "application/json"}
        make_request = requests.patch(f"{self.API_URL}/users/students/"
                                      f"assignedteacher/{id_to_delete}", 
                                      headers=headers)
        make_request
                
        return print("\n***student deleted***\n")


    def search_for_user_by_name(self):
        '''searches for inputted name in given list.'''
        while True:
        
            try:
                print("\n***Search for Teacher or Student***\n")
                
                user_list = self.secure_user.sanitise_input(input("Type 't' to"
                " search for teacher or 's' to search for a student: ")
                .lower())
                
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
                
        
        fname = self.secure_user.sanitise_input(input(f"\nEnter {user_type}'s " 
                                                      f"first name: ")).lower()
            
        lname = self.secure_user.sanitise_input(input(f"\nEnter {user_type}'s " 
                                                      f"last name: ")).lower()
        
        # Search for user in given list then display matching user.
        for user in user_list:
            u_fname = user["fname"].lower()
            u_lname = user["lname"].lower() 
            if u_fname == fname and u_lname == lname:
                return self.view_users_info(user)        

        return print(f"{fname} {lname} has not yet been registered as a "
                     f"{user_type}.")
    

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
            
            # Iterate through student_ids list, inputting each student id to 
            # retrieve their info.     
            i = 0
            while i < len(user["student_ids"]):
                student = self.search_for_user_by_id(user["student_ids"][i], 
                                                     self.student_list) 
                 
                assigned_students_data.append(student)
                 
                i += 1

            student_info = []
            
            # Retrieve data and concatenate into string.
            for student in assigned_students_data:
                                      
                  info = f"\nID: {student['id']}\nFirst name: "
                  info += f"{student['fname']}\nLast name: {student['lname']}"
                  info += f" \nSubject: {student['subject']}\nEmail: "
                  info += f"{student['login_email']}\n"
                  
                  student_info.append(info)
        
            student_info_str = "\n".join(student_info)
        
            return print(f"\n*****{user_type} info*****\n\nName: "
                         f"{user['fname']} {user['lname']}\nID: {user['id']}"
                         f"\nEmail: {user['login_email']}\nSubject: "
                         f"{user['subject']}\nActive lesson ID: "
                         f"{user['current_lesson_id']}"
                         f" \n\n***Assigned students***\n{student_info_str}\n")

        # If user is a student, find assigned teacher. 
        elif "student" in user["login_email"]:
            user_type = "Student"
            for teacher in self.teacher_list:
                if user["assigned_teacher_id"] == teacher["id"]:
                    assigned_teacher = teacher
                    break
    
            return print(f"\n*****{user_type} info*****\n\nName: "
                         f"{user['fname']} " 
                         f"{user['lname']}\nID: {user['id']}\nEmail: "
                         f"{user['login_email']}\nSubject: {user['subject']}"
                         f" \nActive lesson ID: {user['current_lesson_id']}"
                         f" \n\n***Assigned teacher***\nName: "
                         f"{teacher['fname']} {teacher['lname']}\nSubject: "
                         f"{teacher['subject']}\nEmail: "
                         f"{teacher['login_email']}\n")

        else:
            return print("This user has not yet been registered as a teacher"
                         " or student.")


    def view_students(self):
        '''Displays all students and corresponding info.'''

        # Re-load teacher and student list instance variables so that they are
        # up-to-date.
        if self.security:
            self.secure_user.check_limit()
        self.student_list = requests.get(f"{self.API_URL}/student_list", 
                            headers={"Content-Type":"application/json"}).json()
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", 
                            headers={"Content-Type": 
                            "application/json"}).json()            

        students_str = ""

        for student in self.student_list:
            students_str += f"\nName: {student['fname']} {student['lname']}"
            students_str += f"\nID: {student['id']}\nEmail: "
            students_str += f"{student['login_email']}\nSubject: "
            students_str += f"{student['subject']}\nActive lesson ID: "
            students_str += f"{student['current_lesson_id']}\n"                   
        
            for teacher in self.teacher_list:                
                if student["assigned_teacher_id"] == teacher["id"]:
                    assigned_teacher = teacher                                
                    students_str += f"\n***Assigned teacher***\nName: "
                    students_str += f"{assigned_teacher['fname']} "
                    students_str += f"{assigned_teacher['lname']}"
                    students_str += f"\nSubject: "
                    students_str += f"{assigned_teacher['subject']}\nEmail: "
                    students_str += f"{assigned_teacher['login_email']}\n\n--"
                    students_str += "----------------------------------------"
        
        return print(f"\n*****Student info*****\n{students_str}")
        

class Teacher(User):        

    def __init__(self, login_email, password, security_object, security=False, 
                 teacher=True):
        super().__init__(login_email, password, security_object, 
                         security=False, teacher=True)                
        
        self.security = security        
        self.secure_user = security_object    
        self.teacher = teacher
        
        if self.security:
            self.secure_user.check_limit()
        self.assigned_student_names = [requests.get(f"{self.API_URL}/users/"
                                      f"teachers/assignedstudent/{self.id}", 
                                      verify=False, headers={"Content-Type": 
                                      "application/json"}).json()]

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

    def __init__(self, login_email, password, security_object, 
                 security=False, student=True):
        super().__init__(login_email, password, security_object, 
                         security=False, student=True)
                
        self.security = security        
        self.secure_user = security_object    
        self.student = student
        
        if self.security:
            self.secure_user.check_limit()
        self.assigned_teacher = requests.get(f"{self.API_URL}/users/students/"
                                f"assignedteacher/{self.id}", verify=False, 
                                headers={"Content-Type": 
                                "application/json"}).json()
  
    def view_assigned_teacher(self):            
        '''Displays teacher information.'''
        fname = self.assigned_teacher["fname"]
        lname = self.assigned_teacher["lname"]
        email = self.assigned_teacher["login_email"]
        subject = self.assigned_teacher["subject"]
        return print(f"\n*****Assigned {subject} teacher*****\n\nName: {fname}" 
                     f"{lname}\nEmail: {email}\n")                                                           
            

    def upload_homework(self):
        '''Posts a homework file to the API.'''
        
        
        file_path = (input("Enter the file path "
                                             "to the homework file to upload"))
        
        # Check file type for upload so only Word files allowed if security on.
        if self.secure_user.is_a_word_file(file_path):
            # Check file size is under 5MB if security on.
            if self.secure_user.conforms_to_max_file_size(file_path):

                with open(file_path, "rb") as f:
                    files = {"file": f}
            
                    response = requests.post(f"{self.API_URL}/users/students/"
                                            f"{self.login_email}", files=files)
            
                    return print(response.text)
            else:
                
                return print("!!File size exceeds 5MB!!")
        
        else:
                return print("!!Onlly Word file allowed!!")

class Lesson(): 
    
    API_URL = "http://127.0.0.1:5000"
    
    def __init__(self, subject, security=False):
        
        self.subject = subject
        self.subject_to_search = subject.lower
        self.security = security
        
        self.secure_lesson = Security(1, security=self.security)

        if self.security:            
            self.secure_lesson.check_limit()
        self.subject_list_path = requests.get(f"{self.API_URL}/lessons/"
                                 f"{self.subject}", verify=False,
                                 headers={"Content-Type": "application/json"})

        if self.subject_list_path.status_code != 404:
            lessons = self.subject_list_path.json()

        if self.security:
            self.secure_lesson.check_limit()
        self.lessons = requests.get(f"{self.API_URL}/lessons/{self.subject}", 
                                    verify=False, headers={"Content-Type": 
                                    "application/json"}).json()               
        
        self.current_lesson_id = int(self.return_active_lesson_id())
        
        self.new_lesson_id = int(self.current_lesson_id) + 1
        
    def return_active_lesson_id(self):
        '''Returns the current_lesson_id for given user.'''

        latest_lesson_id = 0
        
        for lesson in self.lessons:                        
            
            # Match lesson by given subject then store highes lesson_id value
            # as latest_lesson_id (this will be the current, active lesson).
            if str(lesson["subject"])== str(self.subject):                
                if int(lesson["lesson_id"]) > int(latest_lesson_id):
                    latest_lesson_id = int(lesson["lesson_id"])                                        
                            
        return latest_lesson_id
    

    def format_lesson_output(self, empty_list, lesson_list):
        '''Used in multiple methods to display lesson info appropriately.'''
        
        for lesson in lesson_list:
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
    
        info = f"\nLesson ID: {lesson_ID}\nSubject: {subject}\nTitle: "
        info += f"{title}\n\nInput: {lesson_input}\n\nQuestions: \n"
        info += f"{question_str}\n\n"
        info += f"Answers: \n{answer_str}\n\nGrade: {grade}\n\n"
        info += "____________________________________________________________"
    
        lesson_info_to_return = empty_list.append(info)
        
        return lesson_info_to_return
    
    #### Method called by admin only
    def view_all_lessons(self):
        '''Rertieves all lessons for all teachers.'''
        
        lesson_info_to_return = []
    
        for lesson in self.lessons:
            self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return print(info_str)
        
        
    #### Methods called by teachers and students ####
    def view_all_my_lessons(self):                
        '''Rertieves all lessons for one user.'''
        
        lesson_info_to_return = []
        
        for lesson in self.lessons:
            l_subject = lesson["subject"].lower()
            my_subject = self.subject.lower()
            if l_subject == my_subject: self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return print(info_str)
    

    def change_lesson_content(self, title=None, lesson_input=None, 
                              question_1="", question_2="", 
                              question_3="", question_4="", 
                              question_5="", answer_1="", answer_2="",
                              answer_3="", answer_4="", answer_5="",
                              grade=None):        
        '''Modifies lesson data - used to edit and add question, answers 
        and grades'''                
                
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
            "grade": grade            
        }
        
        headers = {"Content-Type": "application/json"}
        
        if self.security:
            self.secure_lesson.check_limit()
            data_string = json.dumps(new_lesson_data).encode("utf-8")
            new_lesson_data = FERNET.encrypt(data_string)
            response = requests.patch(f"{self.API_URL}/lessons/secure/"
                       f"{self.subject}", headers=headers, 
                       data=new_lesson_data)
            
        else: 
            response = requests.patch(f"{self.API_URL}/lessons/{self.subject}", 
                       headers=headers, json=new_lesson_data)
        
        lesson_info_to_return = []

        # If patch was successful...
        if response.status_code == 200:                 
                        
            # Update self.lessons with data added via API to lesson_list.json
            if self.security:
                self.secure_lesson.check_limit()
                
            self.lessons = requests.get(f"{self.API_URL}/lessons/"
                           f"{self.subject}", headers={"Content-Type": 
                           "application/json"}).json()   

            self.lessons

            self.format_lesson_output(lesson_info_to_return, 
                                      self.retrieve_my_active_lesson())
                        
            info_str = "\n".join(lesson_info_to_return) 
            
            print("\n***Lesson Updated!***\n")
            return print(info_str)
        else:
            return print(("Oops! Something went wrong."))

    def retrieve_my_active_lesson(self):
        '''Find a user's current/latest lesson, ready to pass to format_info
        (to display said lesson appropriately).'''
        
        for lesson in self.lessons:            
            l_subject = lesson["subject"].lower()
            l_id = int(lesson["lesson_id"])
            my_subject = self.subject.lower()
            my_lesson_id = int(self.current_lesson_id)
            if l_subject == my_subject and l_id == my_lesson_id:
                return lesson

    def view_my_active_lesson(self):            
        '''Display a user's current/latest lesson.'''
        
        lesson_info_to_return = []

        format_info = self.format_lesson_output 
        format_info(lesson_info_to_return,self.retrieve_my_active_lesson())
            
        info_str = "\n".join(lesson_info_to_return) 
        
        ("\n***Active lesson***\n")        
        return print(info_str)        
        

    ##### Methods called only by teachers.
    def add_new_lesson(self):
        '''Adds a new lesson, automatically assigning lesson id.'''                
        
        print("\n***New lesson to upload***")
        title = self.secure_lesson.sanitise_input(input("\nEnter a lesson " 
                                                        "title: \n"))
        lesson_input = self.secure_lesson.sanitise_input(input("\nEnter "
                                                        "teacher input: "))
        question_1 = self.secure_lesson.sanitise_input(input("Enter question" 
                                                       "1: "))
        question_2 = self.secure_lesson.sanitise_input(input("Enter question "
                                                             "2: "))
        question_3 = self.secure_lesson.sanitise_input(input("Enter question "
                                                             "3: "))
        question_4 = self.secure_lesson.sanitise_input(input("Enter question "
                                                             "4: "))
        question_5 = self.secure_lesson.sanitise_input(input("Enter question "
                                                             "5: "))
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
        
        # If security activated, monitor and limit API calls, and encrypt
        # data to be sent to secure endpoint.
        if self.security:
            self.secure_lesson.check_limit()
            data_string = json.dumps(new_lesson_data).encode("utf-8")
            new_lesson_data = FERNET.encrypt(data_string)
            response = requests.post(f"{self.API_URL}/lessons/secure/"
                       f"{self.subject}", headers=headers, 
                       data=new_lesson_data)
            
        else:
            response = requests.post(f"{self.API_URL}/lessons/{self.subject}",
                       headers=headers, json=new_lesson_data)
        
        # If post was successful, update self.lesson list with new info and 
        # output lesson data.    
        if response.status_code == 201:
            
            # Update self.lessons with data added via API to lesson_lis.json
            if self.security:
                self.secure_lesson.check_limit()
                
            self.lessons = requests.get(f"{self.API_URL}/lessons/"
                           f"{self.subject}", headers={"Content-Type": 
                           "application/json"}).json()

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
                
                # Ask user which parts of the lesson they wish to change and 
                # default to None or "" so that the endpoint can keep the 
                # values as they were if they detect these None or "" values.
                title_choice = self.secure_lesson.sanitise_input(input("Do you"
                               " want to change the title? Type 'y' or 'n': ")
                               .lower())
                
                if title_choice == "y":
                    title = self.secure_lesson.sanitise_input(input("\nEnter a"
                            " new lesson title: \n"))
                
                else:
                    title = None
                    
                input_choice = self.secure_lesson.sanitise_input(input("Do you"
                               " want to change the teacher input? Type 'y' or"
                               " 'n': ").lower())
                
                if input_choice == "y":
                    lesson_input = self.secure_lesson.sanitise_input(input("\n"
                                                "Enter new teacher input: \n"))
                else:
                    lesson_input = None                    
                
                question_choice_1 = self.secure_lesson.sanitise_input(input("D"
                          "o you want to change question 1? Type 'y' or 'n': ")
                 .lower())
                
                if question_choice_1 == "y":                    
                    question_1 = self.secure_lesson.sanitise_input(input("\nE"
                                                 "nter a new question 1: \n"))
                else:
                    question_1 = ""
                                
                question_choice_2 = self.secure_lesson.sanitise_input(input("D"
                          "o you want to change question 2? Type 'y' or 'n': ")
                 .lower())

                if question_choice_2 == "y":                    
                    question_2 = self.secure_lesson.sanitise_input(input("\nE"
                                                 "nter a new question 2: \n"))
                else:
                    question_2 = ""
                    
                question_choice_3 = self.secure_lesson.sanitise_input(input("D"
                          "o you want to change question 3? Type 'y' or 'n': ")
                 .lower())
                    
                if question_choice_3 == "y":                    
                    question_3 = self.secure_lesson.sanitise_input(input("\nEn"
                                                   "ter a new question 3: \n"))
                else:
                    question_3 = ""
                    
                question_choice_4 = self.secure_lesson.sanitise_input(input("D"
                          "o you want to change question 4? Type 'y' or 'n': ")
                 .lower())
                    
                if question_choice_4 == "y":                    
                    question_4 = self.secure_lesson.sanitise_input(input("\nEn"
                                                   "ter a new question 4: \n"))
                else:
                    question_4 = ""
                    
                question_choice_5 = self.secure_lesson.sanitise_input(input("D"
                          "o you want to change question 5? Type 'y' or 'n': ")
                 .lower())
                    
                if question_choice_5 == "y":                    
                    question_5 = self.secure_lesson.sanitise_input(input("\nEn"
                                                   "ter a new question 5: \n"))
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
                answer_input = self.secure_lesson.sanitise_input
                answer_choice_1 = answer_input(input("Do you want to answer" 
                                  "question 1? Type 'y' or 'n': ").lower())                                

                if answer_choice_1 == "y":                    
                    answer_1 = answer_input(input("\nEnter an answer for "
                               "question 1: \n"))
                else:
                    answer_1 = ""                
                
                answer_choice_2 = answer_input(input("Do you want to answer "
                                  "question 2? Type 'y' or 'n': ")
                 .lower())

                if answer_choice_2 == "y":                    
                    answer_2 = answer_input(input("\nEnter an answer for "
                               "question 2: \n"))
                else:
                    answer_2 = ""
                    
                answer_choice_3 = answer_input(input("Do you want to answer "
                                  "question 3? Type 'y' or 'n': ")
                 .lower())
                    
                if answer_choice_3 == "y":                    
                    answer_3 = answer_input(input("\nEnter an answer for "
                               "question 3: \n"))
                else:
                    answer_3 = ""
                    
                answer_choice_4 = answer_input(input("Do you want to answer "
                                  "question 4? Type 'y' or 'n': ")
                 .lower())
                    
                if answer_choice_4 == "y":                    
                    answer_4 = answer_input(input("\nEnter an answer for "
                               "question 4: \n"))
                else:
                    answer_4 = ""
                    
                answer_choice_5 = answer_input(input("Do you want to answer "
                                  "question 5? Type 'y' or 'n': ")
                 .lower())
                    
                if answer_choice_5 == "y":                    
                    answer_5 = answer_input(input("\nEnter an answer for question "
                               "5: \n"))
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
        self.max_file_size = 5 * 1024 * 1024 # 5MB

    CALLS = 4
    ############ Subtract to show attempts left    

    # Svenheim (2020)
    @sleep_and_retry
    @limits(calls=20, period=60)
    def check_limit(self):
        ''' Empty function just to check for calls to API 
        and lock some out if suspected DDOS attack'''        
        
        return                                                

    @sleep_and_retry
    @limits(calls=4, period=60)
    def password_attempts_check(self):        
        '''Monitors login attempts, limiting to 4, with a 60 second lock-out'''
        
        if self.login_attempts == 4:
            return print(f"\n!!! One login attempt remaining until your"
                         " account is locked !!!\n")            
            
        else:                        
            return
        
        
    def sanitise_input(self, input_str):
        '''Checks to ensure input is not so large it will hang the program.'''
        
        if self.security:
            
            if len(input_str) > 20:
                
                return input_str[0:20]
            
        return input_str                                
       
    
    def is_a_word_file(self, file_path):
        '''Checks whether file for upload is a Word file.'''
        
        if self.security:
            return re.match(r"^.*\.(doc|docx)$", file_path)
        else:
            return True # Bypass check if security is off.


    def initial_password__hash(self, password):
        '''Hashes given password to compare to stored passwords when logging
        in.'''
        
        return hashlib.sha256(password.encode()).hexdigest()
    
    def hash_password(self, password):
        '''Hashes a given password if security activated.'''
        
        if self.security:
            return hashlib.sha256(password.encode()).hexdigest()
        else:
            return password
    
    def conforms_to_max_file_size(self, filepath):
        '''Checks file size of files waiting for upload.'''
        
        if self.security:
            if os.path.getsize(filepath) > self.max_file_size:
                return False
            else:
                return True
        else:
            return True # Return True if security is off and no max file size.
            
################################# Menu classes ###########################

class Menu:
    '''Factory class - children classes inherit options and corresponding 
            methods.'''
            
    def __init__(self, option_1, option_2, method_1, method_2):
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_1 = option_1
        self.option_2 = option_2
                       
        self.method_1 = method_1
        self.method_2 = method_2        

       
class AdminMenu(Menu):
    '''Inherits from Menu and adds extra options and methods.'''

    def __init__(self, option_1, option_2, option_3, option_4, option_5,
                 method_1, method_2, method_3, method_4, method_5):        
        super().__init__(option_1, option_2, method_1, method_2)                                                    
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_3 = option_3
        self.option_4 = option_4
        self.option_5 = option_5
                       
        self.method_3 = method_3
        self.method_4 = method_4        
        self.method_5 = method_5
    
        
    def show_menu(self):
        '''Displays the menu to the users, with options numbers corresponding
           to matching method numbers.''' 
           
        while True:                       
        # presenting the menu to the user and
        # making sure that the user input is converted to lower case.
          print()
          menu = input(f'''Select one of the following Options below:         
                {self.option_1[0].lower()} - {self.option_1}
                {self.option_2[0].lower()} - {self.option_2}
                {self.option_3[0].lower()} - {self.option_3}
                {self.option_4[0].lower()} - {self.option_4}
                {self.option_5[0].lower()} - {self.option_5}      
        :       ''').lower()             
 
          if menu == self.option_1[0].lower():
            self.method_1()               
 
          elif menu == self.option_2[0].lower():
            self.method_2()
          
          elif menu == self.option_3[0].lower():
            self.method_3()               
 
          elif menu == self.option_4[0].lower():
            self.method_4()
            
          elif menu == self.option_5[0].lower():
            self.method_5()
                                    
          else:
            print("\n!! Choose a valid option. !!\n")     
            
class TeacherMenu(AdminMenu):
    '''Inherits from AdminMenu and adds extra options and methods.'''

    def __init__(self, option_1, option_2, option_3, option_4, option_5, 
                 option_6, option_7, method_1, method_2, method_3, method_4,
                 method_5, method_6, method_7):        
        super().__init__(option_1, option_2, option_3, option_4, option_5,
                         method_1, method_2, method_3, method_4, method_5)
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_6 = option_6
        self.option_7 = option_7
                       
        self.method_6 = method_6
        self.method_7 = method_7        
 
    def show_menu(self):
        '''Displays the menu to the users, with options numbers corresponding
           to matching method numbers.''' 
        
        while True:                       
        # presenting the menu to the user and
        # making sure that the user input is converted to lower case.
          print()
          menu = input(f'''Select one of the following Options below:         
                {self.option_1[0].lower()} - {self.option_1}
                {self.option_2[0].lower()} - {self.option_2}
                {self.option_3[0].lower()} - {self.option_3}
                {self.option_4[0].lower()} - {self.option_4}
                {self.option_5[0].lower()} - {self.option_5}
                {self.option_6[0].lower()} - {self.option_6}
                {self.option_7[0].lower()} - {self.option_7}                
        :       ''').lower()             
 
          if menu == self.option_1[0].lower():
            self.method_1()               
 
          elif menu == self.option_2[0].lower():
            self.method_2()
          
          elif menu == self.option_3[0].lower():
            self.method_3()               
 
          elif menu == self.option_4[0].lower():
            self.method_4()
            
          elif menu == self.option_5[0].lower():
            self.method_5()
            
          elif menu == self.option_6[0].lower():
            self.method_6()
          
          elif menu == self.option_7[0].lower():
            self.method_7()                          
                                    
          else:
            print("\n!! Choose a valid option. !!\n")     

class StudentMenu(AdminMenu):
    '''Inherits from AdminMenu without modifying.'''
    
    def __init__(self, option_1, option_2, option_3, option_4, option_5, 
                 method_1, method_2, method_3, method_4, method_5):        
        
        super().__init__(option_1, option_2, option_3, option_4, option_5,
                         method_1, method_2, method_3, method_4, method_5)

        '''Allows for the creation of main menus and sub-menus'''

class LoginMenu():
    
    API_URL = "http://127.0.0.1:5000"
        
    def __init__(self, security=False, attempts=1):
        
        self.security = security
        self.attempts = attempts
        self.login_success = False        
        self.password__is_hashed = False
        self.login_email = ""
        self.password = ""
        self.user_type = ""
        self.hashed_password = ""        

        self.secure_app = Security(self.attempts)
        
        # If security activated by user input, instantiate security object and
        # call method to check login attempts, locking account if more than 4 made.
        if self.security:                                 
            self.secure_app.password_attempts_check()
                                                              
        self.login_process() 
        

    def login_process(self):
        '''Displays the login menu'''                                
                
        self.login_email = str(input("\n* Enter your email address: "))
        # Mask password input.
        self.password = pwinput.pwinput("* Enter your password: ") 
        
        # Hash the password so that it can be compared to the stored hashed 
        # password if security was active when user created.
        self.hashed_password = self.secure_app.initial_password__hash(str(self.password))
        
        # If user identified as admin, API call made to obtain list of admin 
        # users and details.
        if "admin" in str(self.login_email):            
            self.user_type ="admin"
            
            user_list = requests.get(f"{self.API_URL}/admin_list", 
                        headers={"Content-Type":"application/json"}).json()            
                        
        # If user identified as teacher, API call made to obtain list of 
        # teacher users and details.
        elif "teacher" in str(self.login_email):            
            self.user_type ="teacher"
            user_list = requests.get(f"{self.API_URL}/teacher_list",
                        headers={"Content-Type":"application/json"}).json()
        
        # If user identified as teacher, API call made to obtain list of 
        # teacher users and details.
        elif "student" in str(self.login_email):
            self.user_type ="student"
            user_list = requests.get(f"{self.API_URL}/student_list",
                        headers={"Content-Type": "application/json"}).json()
            
        else:
            print("That email address is not valid.", self.attempts)
            
            # If security is activated, monitor login attempts to later pass
            # to security object and password_attempts_check method to ensure
            # account lockout after 4 attempts.
            
            if self.security:
                self.attempts += 1
                
                # Reset once 5 attempts reached, so that counter starts again
                # after lock-out.
                if self.attempts == 6:
                    self.attempts = 1
                    
                new_menu = LoginMenu(security=True, attempts=self.attempts)                

            else:
                new_menu = LoginMenu()
            
                print(f"Login attempts: {self.attempts}")        
                                                    
        # Locate user's login details.
        for user in user_list:            
            stored_email = str(user["login_email"])
            stored_pw = str(user["hashed_password"])                        
            
            # Check length of password. If over 20 characters, password is 
            # hashed and needs to be compared with hashed. If not, password
            # is compared with plaintext password.                                                            
            if stored_email == self.login_email and stored_pw == str(self.hashed_password):
                    
                self.login_success = True                
                self.password__is_hashed = True                                                    
                self.show_menu()

            elif stored_email == self.login_email and stored_pw == self.password:                                        
                
                self.login_success = True                               
                self.show_menu()
                
        # Message to print if email and password not matched.
        print(f"Your {self.user_type} email address or password is incorrect.")
            
        # If security has been activated, count login attempts, ready 
        # to pass to Security class.            
        if self.security:
            self.attempts += 1
        
        # If max login attempts made, reset attempts.
        if self.attempts == 5:
            self.attempts = 1            
        
        # If security has been activated, re-load login menu with security,
        # otherwise, keep it as default (deactivated).    
        if self.security:
            new_menu = LoginMenu(security=True, attempts=self.attempts)
        else:
            new_menu = LoginMenu()
            

    def show_menu(self):            
        '''Displays subsequent menu.'''
            
        # Give user option to turn security on if admin.        
        while True:
            try:
                choice = input("\n***Type 's' to switch Security on," 
                                       " or press 'c'"
                                       " to continue***: ").lower()
                
                if choice == 's' and self.user_type == "admin":
                    self.security = True
                    print("\n***RUNNING IN SECURE MODE***\n")
                    break
                
                elif choice == "s" and self.user_type != "admin":
                    print("\n!!Only administrators can activate" 
                                                " secure mode!!")
                    print("\n!!!RUNNING IN INSECURE MODE!!!\n")
                    break
                
                elif choice == 'c' and self.security == False:
                    print("\n!!!RUNNING IN INSECURE MODE!!!\n")
                    self.security = False
                    break
                
                else:
                    print("\n***RUNNING IN SECURE MODE***\n")
                
            except KeyError:
                
                print("Pick a valid choice!")

        # Instantiate relevant user object to gain access to its 
        # specific methods, passing these to the {user_type} Menu so that 
        # they can be called by the user. If security has been 
        # activated, pass this on to the user object to ensure 
        # security methods are called within user methods.  
        if self.user_type == "admin":
                                                                                                  
            # Set security setting for Security object,
            # so that sanitise_input() method runs if security is 
            # set to True.                   
            self.secure_app.security = self.security
                    
            # If password is stored as hashed (due to security being 
            # when activated when user was created), assign as 
            # self.password when user object created.
            if self.password__is_hashed:

                user = Admin(self.login_email, self.hashed_password, 
                    self.secure_app, security=self.security)
                    
            else:
                        
                user = Admin(self.login_email, self.password, 
                             self.secure_app, security=self.security)
                        

            user_menu = AdminMenu("Profile", "Name search", 
                                  "Enrol new student", 
                                  "Unregister a student", 
                                  "Students", 
                                  user.view_user_profile,                                           
                                  user.search_for_user_by_name, 
                                  user.enrol_student, 
                                  user.delete_student, 
                                  user.view_students)
                    
            user_menu.show_menu() # Move user on to their user menu.                                        
                    
        elif self.user_type == "teacher":
                                                            
            self.secure_app.security = self.security 
                    
            if self.password__is_hashed:
                        
                user = Teacher(self.login_email, self.hashed_password, 
                                   self.secure_app, security=self.security)
                    
            else:
                user = Teacher(self.login_email, self.password, 
                               self.secure_app, security=self.security)

            # Lesson object instantiated to give non-admin user access
            # to lesson methods.
            lesson = Lesson(user.subject, security=self.security)
                    
            user_menu = TeacherMenu("Profile", "View my students",
                                    "My lessons", "Current lesson",
                                    "New lesson", "Update lesson",
                                     "Assign grade", user.view_user_profile,                                            
                                     user.view_assigned_students, 
                                     lesson.view_all_my_lessons,
                                     lesson.view_my_active_lesson,
                                     lesson.add_new_lesson, 
                                     lesson.update_lesson,
                                     lesson.assign_grade)                                        
                    
            user_menu.show_menu()   
                    
        elif self.user_type == "student":
                    
            self.secure_app.security = self.security
                    
            if self.password__is_hashed:
                    
                user = Student(self.login_email, self.hashed_password, 
                               self.secure_app, security=self.security)
                    
            else:
                user = Student(self.login_email, self.password, 
                               self.secure_app, security=self.security)                                        

                                        
            lesson = Lesson(user.subject, security=self.security)

            user_menu = StudentMenu("Submit homework", "View my teacher",
                                    "My lessons", "Current lesson",
                                    "Submit answers",
                                    user.upload_homework, 
                                    user.view_assigned_teacher,
                                    lesson.view_all_my_lessons,
                                    lesson.view_my_active_lesson,   
                                    lesson.add_answers)
                    
            user_menu.show_menu()                            
        
        


########### Program initialisation ################

# Instantiate the login menu as first screen of the program.
new_menu = LoginMenu()

# To test how login deals with Brute Force attack, uncomment the line below.
# new_menu = LoginMenu(security=True)
    
    