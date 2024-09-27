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


login_email = input("Enter your email address: ")
student_id =  requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["student_id"]
fname = requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["fname"]
lname = requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["lname"]
DOB = requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["DOB"]
subject_studying = requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["subject_studying"]
lesson_id = requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["lesson_id"]
assigned_teacher_id = int(requests.get(f"{API_URL}/users/students/{login_email}", headers={"Content-Type": "application/json"}).json()["assigned_teacher_id"])
assigned_teacher = view_assigned_teacher(student_id)
print(f"\nName: {fname} {lname}\nDOB: {DOB}\nStudying: {subject_studying}\nlesson id: {lesson_id}\n{assigned_teacher}")