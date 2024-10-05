import requests
####NOTES########

# Avoid API injection by adding hashed code to endpoints?
#logging on instantiates object - email used as input to get instance variables used within methods.
## Update student keys - assigned_teacher_id - automate
# Change student key to assigned teacher?
## Make admin endpoints to match __init__ variables


# When admin registers a new teacher, student ids are empty but when they assign a new student, if subjects match and student ids are less than 3, they're assigned to first one and teacher student_ids are updated.
# Extend teacher and student version of view user_profile (Super? Extends?) to include subject teaching/studying assigned students/teacher.


# Admin/Teacher/Student menus and sub-menus
# Security options


# Finish lesson class methods.

# Change 'current_lesson_id' to 'active_lesson_id'. 

# Use similar method to return_active_lesson_id to get latest teacher and student ids, then increment, ready to automatically assign new id when setting up new user.

# *** modify_lesson_content used to cover multiplle methods *** #

###### Change data structure of lessons dict - Qs and As as lists. - then change format_lesson_output() method to account for this change.
####### CHange lesson IDs
class User():
    
    API_URL = "http://127.0.0.1:5000"
    
    def __init__(self, login_email, password):
        admin = False
        teacher = False
        student = False                
        
        self.login_email = login_email 
        self.password = password                        
        
        if admin:
            user = "admin"
        elif teacher:
            user = "teacher"
        else:
            user = "student"
        
        ################# Adjust for PEP-8?
        self.user_info = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()     
        self.id =  self.user_info["id"]
        self.fname = self.user_info["fname"]
        self.lname = self.user_info["lname"]
        self.DOB = self.user_info["DOB"]                

        if not admin:    
            self.current_lesson_id = self.user_info["current_lesson_id"]
            self.subject = self.user_info["subject"]
                
    def view_user_profile(self): # Add lesson details
        
        return f"\t\t****{self.user} profile****\n\nName: {self.fname} {self.lname}\n{self.user} ID: {self.id}\nEmail: {self.email}\nDate of Birth: {self.DOB}"
                                                   

class Admin(User):    
    
    admin = True    

    def __init__(self):
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()
        self.student_list = requests.get(f"{self.API_URL}/student_list", headers={"Content-Type": "application/json"}).json()

    def register_teacher(self, ALLFIELDS): #POST
        #Pass args - see example.
        # Assigned student_ids blank at first?
        pass        

    def assign_teacher(self, teacher): #PATCH to student  
        pass        
        

    def user_search_by_name(self, fname, lname, user_list):
        '''searches for inputted name in given list.'''
    
        if str(user_list)== "teacher_list":
            user_type = "teacher"
        elif str(user_list)== "student_list":
            user_type = "student"
    
        for user in user_list:
            if user["fname"] == fname and user["lname"] == lname:
                    return user
        
        return f"{fname} {lname} has not yet been registered as a {user_type}."
    
    def user_search_by_id(id, user_list):
        '''Searches for user by id in given list.'''
        for user in user_list:        
            if int(user["id"]) == id:
                return user
    
    def view_users_info(self, user):
        '''Displays teacher or student information.'''
        # If user is a teacher, find assigned students.
        if "teacher" in user["login_email"]:
            user_type = "teacher"    
            assigned_students_data = []     
             # Iterate through student_ids list, inputting each student id to retrieve their info.     
            i = 0
            while i < len(user["student_ids"]):
                student = self.user_search_by_id(user["student_ids"][i], self.student_list) 
                 
                assigned_students_data.append(student)
                 
                i += 1

            student_info = []
            for student in assigned_students_data:
                                      
                  info = f"\nID: {student['id']}\nFirst name: {student['fname']}\nLast name: {student['lname']}\nSubject: {student['subject']}\nEmail: {student['login_email']}\n"
                  student_info.append(info)
        
            student_info_str = "\n".join(student_info)
        
            return f"\n*****{user_type} info*****\n\nName: {user['fname']} {user['lname']}\nID: {user['id']}\nEmail: {user['login_email']}\nSubject: {user['subject']}\nActive lesson ID: {user['current_lesson_id']}\n\n***Assigned students***\n{student_info_str}\n"

        # If user is a student, find assigned teacher. 
        elif "student" in user["login_email"]:
            user_type = "student"
            for teacher in self.teacher_list:
                if user["assigned_teacher_id"] == teacher["id"]:
                    assigned_teacher = teacher
                    break
    
            return f"\n*****{user_type} info*****\n\nName: {user['fname']} {user['lname']}\nID: {user['id']}\nEmail: {user['login_email']}\nSubject: {user['subject']}\nActive lesson ID: {user['current_lesson_id']}\n\n***Assigned teacher***\nName: {teacher['fname']} {teacher['lname']}\nSubject: {teacher['subject']}\nEmail: {teacher['login_email']}\n"

        else:
            return "This user has not yet been registered as a teacher or student."
        


    def delete_teacher(self, teacher_fname, teacher_lname): #DELETE
        # Will have to delete teacher ids in assigned student key, then will have to prompt to assign new teacher to these.
        pass

    def enrol_student(self, student): #PUT then #PATCH(assign to teacher's student_ids (append))
        # assigned teacher_id blank at first?
        pass

    def assign_student(self, student): #PATCH ################## separate method??????
        # Will have to check which subject chosen and assign to appropriate teacher.
        pass

    def search_student(self, student_fname, student_lname): #GET
        pass
    
    

    def delete_student(self, student_fname, student_lname): #DELETE
        # Will have to delete student ids in assigned teacher key, then will have to prompt if teacher has no more students - more students needed!
        pass

    def view_students(self): #GET ###########CHange
        headers = {"Content-Type": "application/json"}  
        response = requests.get(f"{self.API_URL}/'student_list'", headers=headers)
        data = response.json()        
        student_details = [(student["student_id"], student["fname"], student["lname"], student["email"]) for student in data]
        return(student_details)

class Teacher(User):
    
    def __init__(self):
        teacher = True
                        
        self.assigned_student_names = [requests.get(f"{self.API_URL}/users/teachers/{self.id}/assignedstudent", headers={"Content-Type": "application/json"}).json()]

    def view_assigned_students(self):                                
            
        student_str = ""

        student_num = 1
        for student in self.assigned_student_names:
            for name in student:
                    
                student_str += f"\nStudent {student_num}: {name}\n"
                student_num +=1                                
            
        return f"\n*****Assigned students*****\n\n{student_str}"                                        
        

class Student(User):
    
    def __init__(self):    
        student = True
                
        self.assigned_teacher = requests.get(f"{self.API_URL}/users/students/{self.id}/assignedteacher", headers={"Content-Type": "application/json"}).json()
  
        def view_assigned_teacher():            
            
            fname = self.assigned_teacher["fname"]
            lname = self.assigned_teacher["lname"]
            email = self.assigned_teacher["login_email"]
            subject = self.assigned_teacher["subject"]
            return f"\n*****Assigned {subject} teacher*****\n\nName: {fname} {lname}\nEmail: {email}\n"
                                                   
   
class Lesson():
        
    def __init__(self, subject):
        
        self.subject = subject

        self.lessons = requests.get(f"{self.API_URL}/users/{subject}/lesson_id", 
                                             headers={"Content-Type": "application/json"}).json()               
        
        self.current_lesson_id = self.return_active_lesson_id(subject)
        
        self.new_lesson_id = int(self.current_lesson_id) + 1 # Increment latest lesson id by 1 to ensure new lesson id is unique and follows on.
    
    def return_active_lesson_id(self, subject):
        
        latest_lesson_id = 0
        
        for lesson in self.lessons:
            if lesson["subject"].lower() == subject.lower():                
                if int(lesson["lesson_id"]) > latest_lesson_id:
                    latest_lesson_id = lesson["lesson_id"]                    
        
        return latest_lesson_id
            

    def format_lesson_output(self, empty_list, lesson_list):
        lesson_ID = lesson_list["lesson_id"]
        subject = lesson_list["subject"]
        title = lesson_list["title"]
        lesson_input = lesson_list["input"]
        questions = "\n".join(f"{q}) {text}" for q, text in lesson_list["questions"].items())
        answers = "\n".join(f"{a}) {text}" for a, text in lesson_list["answers"].items()) 
        grade = lesson_list["grade"]    
    
        info = f"\nLesson ID: {lesson_ID}\nSubject: {subject}\nTitle: {title}\nInput: {lesson_input}\nQuestions: \n{questions}\nAnswers: \n{answers}\nGrade: {grade}"
    
        lesson_info_to_return = empty_list.append(info)
        return lesson_info_to_return
    
    #### Method called by admin only
    def view_all_lessons(self):
            
        lesson_info_to_return = []
    
        for lesson in self.lessons:
            self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return info_str
    
    
    #### Methods called by teachers and students #########
    def view_all_my_lessons(self, subject):                
        
        lesson_info_to_return = []

        for lesson in self.lessons:
            if lesson["subject"].lower() == subject.lower():
                self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return info_str

    def view_my_active_lesson(self, subject, current_lesson_id):            
        
        lesson_info_to_return = []

        for lesson in self.lessons:
            if lesson["subject"].lower() == subject.lower() and current_lesson_id == lesson["lesson_id"]:
                self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return) 
        return info_str    
        
    def change_lesson_content(self, subject, lesson_id, title=None, question_1=None, question_2=None, 
                       question_3=None, question_4=None, question_5=None, answer_1=None, answer_2=None, 
                       answer_3=None, answer_4=None, answer_5=None, grade=None):
    
        new_lesson_data = {
            "lesson_id": lesson_id,
            "subject": subject,        
            "title": title,        
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
        response = requests.patch(f"{self.API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
        if response.status_code == 201:
        
            return(response.json())
        
    ##### Methods called only by teachers.
    def add_new_lesson(self, subject, title, lesson_input, question_1=None, question_2=None, question_3=None, question_4=None, question_5=None):
     new_lesson_data = {
        "lesson_id": self.new_lesson_id,
        "subject": subject,
        "title": title,
        "input": lesson_input,
        "questions": {
            "1": question_1,
            "2": question_2,
            "3": question_3,
            "4": question_4,
            "5": question_5
        },
        "answers": {
            "1": "None",
            "2": "None",
            "3": "None",
            "4": "None",
            "5": "None"
             },
        "grade": "None"
        }
     headers = {"Content-Type": "application/json"}  
     response = requests.post(f"{self.API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
     if response.status_code == 201:
        
        return(response.json())
     
     return("Oops! Something went wrong.")
                              

    

    
   
    
    