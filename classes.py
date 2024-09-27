import requests
####NOTES########
#admin creates student object, calls register method with todd.fname etc
#If student logs on, how are their methods called when, for example answering questons? API searches automaticalley for self.fname etc
#...and displays lesson questions. view_questions method needed; submit_answer meethod needed - edit_answer()?

#logging on instantiates object - email used as input to get instance variables used within methods.
## Update student keys - assigned_teacher_id - automate
# Change student key to assigned teacher?
## Make admin endpoints to match __init__ variables
##Change subject_studied to subject so teachers and students can share
# Admin only assign to main subjects - error handling
# When admin registers a new teacher, student ids are empty but when they assign a new student, if subjects match and student ids are less than 3, they're assigned to first one and teacher student_ids are updated.
class User():
    
    API_URL = "http://127.0.0.1:5000"
    
    def __init__(self, login_email, password):
        admin = False
        teacher = False
        student = False                
        
        self.login_email = login_email 
        self.password = password                        
        
        if admin:
            user_path = "admin"
        elif teacher:
            user_path = "teachers"
        else:
            user_path = "students"
        
        ################# Adjust for PEP-8?
        self.id =  requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["id"]
        self.fname = requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["fname"]
        self.lname = requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["lname"]
        self.DOB = requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["DOB"]
        self.subject = requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["subject"]
        
        if not admin:    
            self.lesson_id = requests.get(f"{self.API_URL}/users/{user_path}/{self.login_email}", headers={"Content-Type": "application/json"}).json()["lesson_id"]

    def view_user_info(self): # Add lesson details
        # Admins calling this method view all teacher info.
        if self.admin:
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/'teacher_list'", headers=headers)
            data = response.json()        
            teacher_details = [(teacher["teacher_id"], teacher["fname"], teacher["lname"], teacher["email"]) for teacher in data]
            return(teacher_details)
        # Teachers calling this method view their own info.
        elif self.teacher:                                
        
            return f"Name: {self.fname} {self.lname}\nEmail: {self.email}\n"
        # Students calling this method view their assigned teacher info.    
        else: 
            data = {"student_id": self.student_id}
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/users/students/{self.student_id}/assignedteacher", headers=headers, json=data)
            response = response.json()
    
            assigned_teacher_fname = response["fname"]
            assigned_teacher_lname = response["lname"]
            assigned_teacher_email = response["login_email"]
            return f"Assigned teacher: {assigned_teacher_fname} {assigned_teacher_lname}\nTeacher's email: {assigned_teacher_email}\n"

    def view_student_info(self):
        # Admins calling this method view all student info.
        if self.admin:
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/'student_list'", headers=headers)
            data = response.json()        
            student_details = [(student["student_id"], student["fname"], student["lname"], student["email"]) for student in data]
            return(student_details)
        
        # Teachers calling this method view their assigned student info.    
        elif self.teacher:
            data = {"teacher_id": self.teaceher_id}
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/users/teachers/<int:teacher_id>/assignedstudent", headers=headers, json=data)
            response = response.json()
            ################################################### WIll need to iterate through list
            assigned_student_fname = response["fname"]
            assigned_student_lname = response["lname"]
            assigned_student_email = response["login_email"]
            return f"Assigned student: {assigned_student_fname} {assigned_student_lname}\nTeacher's email: {assigned_student_email}\n"
        # Students calling this method view their own user info.            
        else:             
            data = {"fname": self.fname,
                    "lname": self.lname}
            headers = {"Content-Type": "application/json"}  
            response = requests.get(f"{self.API_URL}/students/{self.lname}", headers=headers, json=data)
            response = response.json()
            
            fname = response["fname"]
            lname = response["lname"]
            email = response["login_email"]
            
            return f"Name: {fname} {lname}\nEmail: {email}\n"
            # Add lesson details                
        
class Admin(User):    
    
    admin = True

    def register_user(self, user):        
        
        
        
class Teacher(User):
    
    def __init__(self):
        teacher = True
                        
        self.student_ids = requests.get(f"{self.API_URL}/users/teachers/{self.login_email}", headers={"Content-Type": "application/json"}).json()["student_ids"]
        

class Student(User):
    
    def __init__(self):    
        student = True
                                
        self.assigned_teacher_id = requests.get(f"{self.API_URL}/users/students/{self.login_email}", headers={"Content-Type": "application/json"}).json()["assigned_teacher_id"]        
  
    
    

   

class Student():
              
    #iterate through teacher list to find teacher then disply
    
    def view_teacher(self):
        
        return(f"{t['fname']} {t['lname']} is your teacher. You can reach them at {t['login_email']}")
            
            
        
#teacher_test = Teacher()
#student_1 = Student("student1@school.co.uk", "hsiohji9", 900, "Dane", "Bowers", "11.02,85", 1, 1)

