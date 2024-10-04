import requests

API_URL = "http://127.0.0.1:5000"


def cli():
    '''A CLI to intearact with the Flask API.'''
    pass


    
def view_user_list(user_list):
    headers = {"Content-Type": "application/json"}  # Set the correct content type
    response = requests.get(f"{API_URL}/{user_list}", headers=headers)
    data = response.json()
    
    if user_list == "student_list":
        student_details = [(student["student_id"], student["fname"], student["lname"]) for student in data]
        print(student_details)
    elif user_list == "teacher_list":
        teacher_details = [(teacher["teacher_id"], teacher["fname"], teacher["lname"]) for teacher in data]
        print(teacher_details)

def return_active_lesson_id(subject):
        lessons = requests.get(f"{API_URL}/lessons",headers={"Content-Type": "application/json"}).json()
        
        latest_lesson_id = 0

        for lesson in lessons:
            if lesson["subject"].lower() == subject.lower():                
                if int(lesson["lesson_id"]) > latest_lesson_id:
                    latest_lesson_id = lesson["lesson_id"]
                    
        
        return latest_lesson_id


'''subject = input("Enter subject: ")
title = input("Enter title: ")
lesson_input = input("Enter lesson input: ")
question_1 = input("Enter question 1: ")
question_2 = input("Enter question 2: ")
        
           
        
current_lesson_id = return_active_lesson_id(subject)
        
new_lesson_id = int(current_lesson_id) + 1 # Increment latest lesson id by 1 to ensure new lesson id is unique and follows on.'''

'''def add_new_lesson(subject, title, lesson_input, question_1=None, question_2=None, question_3=None, question_4=None, question_5=None):
     new_lesson_data = {
        "lesson_id": new_lesson_id,
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
            "1": None,
            "2": None,
            "3": None,
            "4": None,
            "5": None
             },
        "grade": None
        }
     headers = {"Content-Type": "application/json"}  # Set the correct content type    
     response = requests.post(f"{API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
     if response.status_code == 201:
        
        return(response.json())
     
     return("Oops! Something went wrong.")'''

#print(add_new_lesson(subject, title, lesson_input, question_1, question_2))
 

def add_lesson_answers(subject, lesson_id, title=None, question_1=None, question_2=None, 
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
    response = requests.patch(f"{API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
    if response.status_code == 201:
        
        return(response.json())
     

    return("Oops! Something went wrong.")

print(add_lesson_answers("English", 1, title="Eng", question_1="Test", question_2="where", 
                       question_3="anything", question_4=None, question_5=None, answer_1="test1", 
                       answer_2="test2", answer_3="test3", answer_4="test4", answer_5="test5", grade="A"))

#print(add_lesson_answers("English", 1, 4, 3, 2, 1, 8))

'''def add_lesson_answers(subject):
     new_lesson_data = {        
        "subject": subject,
        "answers": {
            "1": subjec t
            }
     }
     headers = {"Content-Type": "application/json"}  
     response = requests.patch(f"{API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
     if response.status_code == 201:
        
        return(response.json())
     , "test"
     return("Oops! Something went wrong.")
print(add_lesson_answers("English"))'''

add_lesson_answers("English", 1, "test1", "test2", "test3", "test4", "test5")

def add_new_teacher(first_name, last_name, DOB):
    new_user_data = {
        "fname": first_name,
        "lname": last_name,
        "login_email": "teacher1@school.co.uk",                  
        "hashed_password": "hsiohji9",
        "teacher_id": 3,        
        "DOB": str(DOB),
        "lesson_id": 1,
        "student_ids": [907, 908, 909]
        }
    headers = {"Content-Type": "application/json"}  # Set the correct content type    
    response = requests.post(f"{API_URL}/users/user/{first_name}", headers=headers, json=new_user_data)
    if response.status_code == 201:
        print("New user added successfully!")
        print(response.json())
    else:
        print("Oops! Something went wrong.")



'''first_name = input("Enter first name: ")
last_name = input("Enter last name: ")

DOB = input("Input date of birth (DD/MM/YY): ")
view_user(first_name, last_name)'''
#add_new_teacher(first_name, last_name, DOB)

'''user_list = input("Enter teacher or student: ")
view_user_list(user_list + "_list")'''

'''def view_student(student_fname, student_lname):
        data = {"fname": student_fname,
                "lname": student_lname}
        headers = {"Content-Type": "application/json"}  
        response = requests.get(f"{API_URL}/users/students/{student_lname}", headers=headers, json=data)
        response = response.json()
        
        first_name = response["fname"]
        last_name = response["lname"]
        email = response["login_email"]
        
        return f"Name: {first_name} {last_name}\nEmail: {email}\n"
                                 
def get_student_id(student_fname, student_lname):
    data = {"fname": student_fname,
            "lname": student_lname}
    headers = {"Content-Type": "application/json"}  
    response = requests.get(f"{API_URL}/users/students/{student_lname}", headers=headers, json=data)
    response = response.json()
    
    return response["student_id"]
    
def admin_menu():
    login_email = input("Assign an email address to this user: ") #need a way for user to input this themselves
        
        password = input("Assign a password for this user: ") #need a way for user to input this themselves
        if user == "teacher":
            teacher_id = input("Assign a teacher id to this user: ") #needs to be automated e.g. self.latest_teacher_id += 1
            student_ids = [input("Assign student ids to this teacher, separated with a comma: ")] #needs to be a choice with current student_ids assignments detailed
        else:
            student_id = input("Assign a student id to this user: ")
            assigned_teacher_id = input("Assign a teacher id for this user: ")
        fname = input("Assign a password for this user: ")
        lname = input("Assign a password for this user: ")
        DOB = input("Assign a password for this user: ")
        lesson_id = input("Assign a password for this user: ") #needs choice with options detailed
    if user == "teacher":
            new_teacher = Teacher(login_email, password, fname, lname, DOB, lesson_id, teacher_id=teacher_id, student_ids=student_ids)
        else:
            new_student = Student(login_email, password, fname, lname, DOB, lesson_id, assigned_teacher_id=assigned_teacher_id, student_ids=student_ids)'''

    
    
    

'''student_fname = input("Enter first name of student to view: ")
student_lname = input("Enter last name of student to view: ")'''

'''print(view_student(student_fname, student_lname))
student_id = int(get_student_id(student_fname, student_lname))
print(student_id)
print(view_assigned_teacher(student_lname, 908))'''

def view_assigned_teacher(student_id):
    data = {"student_id": student_id}
    headers = {"Content-Type": "application/json"}  
    response = requests.get(f"{API_URL}/users/students/{student_id}/assignedteacher", headers=headers, json=data)
    response = response.json()
    
    assigned_teacher_fname = response["fname"]
    assigned_teacher_lname = response["lname"]
    assigned_teacher_email = response["login_email"]
    return f"Assigned teacher: {assigned_teacher_fname} {assigned_teacher_lname}\nTeacher's email: {assigned_teacher_email}\n"    

def view_users(user): #GET
        
        ######## Insert logic to handle 'user' input - must be strictly 'student' or 'teacher'.
        headers = {"Content-Type": "application/json"}  
        response = requests.get(f"{API_URL}/{user}_list", headers=headers)
        data = response.json()        
        user_details = [(user["id"], user["fname"], user["lname"], user["login_email"]) for user in data]
               
        info_to_return = []
        # Iterate through user details and output each field.
        for detail_line in user_details:            
              ID, fname, lname, uname = detail_line
              
              info = f"\nID: {ID}\nFirst name: {fname}\nLast name: {lname}\nUsername: {uname}\n"
              info_to_return.append(info)
        
        info_str = "\n".join(info_to_return)
              
        return info_str

def login(email, password):
    password_attempts_remaining = 5
    data = {"login_email": email}
    headers = {"Content-Type": "application/json"}      
    # conditions based on whether email contains the word admin, student or teacher, calling different URIs
    
    # Assign 'users' variable to be used as dynamic variable in API URI so that all 3 user lists can be accessed
    # depending on user type (detailed in email).
    if "admin" in str(email): 
        users = "admins"
        admin = True
        
    elif "teacher" in str(email):        
        users = "teachers"
    
    else: 
        users = "students"
        
    response = requests.get(f"{API_URL}/users/{users}/{email}", headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        returned_email = response_data["login_email"]
        returned_password = response_data["hashed_password"]

        if password == returned_password and admin:
            print("You're in!")
            return (view_users("teacher"))
            # Call sub-menu depending on list
        

        else:
            password_attempts_remaining -= 1                            
            return f"Incorrect password. {password_attempts_remaining} password attempts remaning." #### Security feature
    
    return "This email address has not been registered. Contact your administrator."

    


def format_lesson_output(empty_list, lesson_list):
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
        
def view_all_lessons():
    lessons = requests.get(f"{API_URL}/lessons",headers={"Content-Type": "application/json"}).json()    
    
    lesson_info_to_return = []
    
    for lesson in lessons:
        format_lesson_output(lesson_info_to_return, lesson)
        
    info_str = "\n".join(lesson_info_to_return)

    return info_str
    
def view_all_my_lessons(subject):
        lessons = requests.get(f"{API_URL}/lessons",headers={"Content-Type": "application/json"}).json()    
        
        lesson_info_to_return = []

        for lesson in lessons:
            if lesson["subject"].lower() == subject.lower():
                format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return info_str

def view_my_active_lesson(subject, current_lesson_id):
        lessons = requests.get(f"{API_URL}/lessons",headers={"Content-Type": "application/json"}).json()    
        
        lesson_info_to_return = []

        for lesson in lessons:
            if lesson["subject"].lower() == subject.lower() and current_lesson_id == lesson["lesson_id"]:
                format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return) 
        return info_str
        
 


'''teacher_info = requests.get(f"{API_URL}/users/teachers/teacher2@school.co.uk", headers={"Content-Type": "application/json"}).json() 
teacher_id = int(teacher_info["id"])
student_ids = teacher_info ["student_ids"]

assigned_student_names = [requests.get(f"{API_URL}/users/teachers/{teacher_id}/assignedstudent", headers={"Content-Type": "application/json"}).json()]'''

'''def view_assigned_students():                                
            
    student_str = ""

    student_num = 1
    for student in assigned_student_names:
        for name in student:
                    
            student_str += f"\nStudent {student_num}: {name}\n"
            student_num +=1                                
            
    return f"\n*****Assigned students*****\n\n{student_str}"

assigned_teacher = requests.get(f"{API_URL}/users/students/905/assignedteacher", headers={"Content-Type": "application/json"}).json()    
  
def view_assigned_teacher():            
            
            fname = assigned_teacher["fname"]
            lname = assigned_teacher["lname"]
            email = assigned_teacher["login_email"]
            subject = assigned_teacher["subject"]
            return f"\n*****Assigned {subject} teacher*****\n\nName: {fname} {lname}\nEmail: {email}\n"'''
#print(view_all_lessons())

#print(view_all_my_lessons("maths"))

#print(view_my_active_lesson("matHs", 3))

#print(return_active_lesson_id("maths"))

#print(view_assigned_students())

#print(view_assigned_teacher())







'''subject = input("subject")

lesson = requests.get(f"{API_URL}   /{subject}/current_lesson_id", 
                                             headers={"Content-Type": "application/json"}).json()               
current_lesson_id = lesson["lesson_id"]
        
new_lesson_id = int(current_lesson_id) + 1 # Increment latest lesson id by 1 to ensure new lesson id is unique and follows on.

print(lesson)
print(current_lesson_id)
print(new_lesson_id)'''

'''while True:
    user = input("Type 's' to view students or 't' to view teachers: ")
    if user == "t":
        user = "teacher"
        break
    elif user == "s":
        user = "student"
        break
    
    #print("Type 's' or 't'.")
        
print(view_users(user))'''

'''login_email = input("Enter your email address: ")
password = input("Enter you password: ")

print(login(login_email, password))'''