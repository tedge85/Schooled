import requests
####NOTES########


# Avoid API injection by adding hashed code to endpoints?
#logging on instantiates object - email used as input to get instance variables used within methods.
## Update student keys - assigned_teacher_id - automate
# Change student key to assigned teacher?
## Make admin endpoints to match __init__ variables
##Change subject_studied to subject so teachers and students can share /

# When admin registers a new teacher, student ids are empty but when they assign a new student, if subjects match and student ids are less than 3, they're assigned to first one and teacher student_ids are updated.
# Extend teacher and student version of view user_profile (Super? Extends?) to include subject teaching/studying assigned students/teacher.

# Login menu
# Admin/Teacher/Student menus and sub-menus
# Security options

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
        self.id =  requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["id"]
        self.fname = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["fname"]
        self.lname = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["lname"]
        self.DOB = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["DOB"]                

        if not admin:    
            self.lesson_id = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["lesson_id"]
            self.subject = requests.get(f"{self.API_URL}/users/{user}s/{self.login_email}", headers={"Content-Type": "application/json"}).json()["subject"]
                
    def view_user_profile(self): # Add lesson details
        
        return f"\t\t****{self.user} profile****\n\nName: {self.fname} {self.lname}\n{self.user} ID: {self.id}\nEmail: {self.email}\nDate of Birth: {self.DOB}"
                                               
    def view_lesson_questions(self):
            pass
    
    def view_lesson_answers(self):
            pass

class Admin(User):    
    
    admin = True    

    def register_teacher(self, ALLFIELDS): #POST
        #Pass args - see example.
        # Assigned student_ids blank at first?
        pass        

    def assign_teacher(self, teacher): #PUT   
        pass        
    
    def view_teachers(self): #GET
        
        headers = {"Content-Type": "application/json"}  
        response = requests.get(f"{self.API_URL}/'teacher_list'", headers=headers)
        data = response.json()        
        teacher_details = [(teacher["teacher_id"], teacher["fname"], teacher["lname"], teacher["email"]) for teacher in data]
        return(teacher_details)
    
    def delete_teacher(self, teacher_fname, teacher_lname): #DELETE
        # Will have to delete teacher ids in assigned student key, then will have to prompt to assign new teacher to these.
        pass

    def enrol_student(self, student): #PUT
        # assigned teacher_id blank at first?
        pass

    def assign_student(self, student): #PUT
        pass

    def search_student(self, student_fname, student_lname): #GET
        pass

    def delete_student(self, student_fname, student_lname): #DELETE
        # Will have to delete student ids in assigned teacher key, then will have to prompt if teacher has no more students - more students needed!
        pass

    def view_students(self): #GET                
        headers = {"Content-Type": "application/json"}  
        response = requests.get(f"{self.API_URL}/'student_list'", headers=headers)
        data = response.json()        
        student_details = [(student["student_id"], student["fname"], student["lname"], student["email"]) for student in data]
        return(student_details)

class Teacher(User):
    
    def __init__(self):
        teacher = True
                        
        self.student_ids = requests.get(f"{self.API_URL}/users/teachers/{self.login_email}", headers={"Content-Type": "application/json"}).json()["student_ids"]
        self.assigned_student_fnames = [requests.get(f"{self.API_URL}/users/teachers/{self.teacher_id}/assignedstudent", headers={"Content-Type": "application/json"}).json()["fname"]]
        self.assigned_student_fnames = [requests.get(f"{self.API_URL}/users/teachers/{self.teacher_id}/assignedstudent", headers={"Content-Type": "application/json"}).json()["lname"]]
        #### need to zip both lists together then have method to  display both names#########
        
        def view_assigned_students(self): ##### GET
            pass                
        
        def upload_lesson_content(self, lesson_id, title, input, questions): ##### POST
            pass
        
        def view_lesson_content(self, lesson_id): ###GET
            pass         
        
        def edit_lesson_questions(self, title=None, input=None, questions=None): ####### POST
            pass
        
        def assign_grade(self, lesson_id): ###### PUT
            pass
        

        

class Student(User):
    
    def __init__(self):    
        student = True
                                
        self.assigned_teacher_id = requests.get(f"{self.API_URL}/users/students/{self.login_email}", headers={"Content-Type": "application/json"}).json()["assigned_teacher_id"]        
  
        def view_assigned_teacher(self):
            data = {"fname": self.fname,
                    "lname": self.lname}
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/students/{self.lname}", headers=headers, json=data) ############### May need to change this URI.
            response = response.json()
            
            fname = response["fname"]
            lname = response["lname"]
            email = response["login_email"]
            
            return f"Name: {fname} {lname}\nEmail: {email}\n"
    
        def view_lesson_questions(self, subject, lesson_id): ##### GET
            pass
        
        def add_lesson_answers(self, subject, lesson_id, answers): ####### PUT
            pass

        def edit_lesson_answers(self, subject, lesson_id, answers): ####### PUT
            pass
            
            
   
