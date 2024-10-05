import requests

API_URL = "http://127.0.0.1:5000"

'''def modify_lesson(subject, lesson_id, title=None, question_1=None, question_2=None, 
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

print(add_lesson_answers("English", 1, title="NEW", question_1="CHANGE?", question_2="where", question_3="anything", 
                         question_4="another test", question_5="and another", answer_1="ANYTHING", answer_2="test2", 
                         answer_3="test3", answer_4="test4", answer_5="ANYTHING NOW?", grade="A"))'''
                         
teacher_list = requests.get(f"{API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()
student_list = requests.get(f"{API_URL}/student_list", headers={"Content-Type": "application/json"}).json()

def user_search_by_name(fname, lname, user_list):
    '''searches for inputted name in given list.'''
    
    if str(user_list)== "teacher_list":
        user_type = "teacher"
    elif str(user_list)== "student_list":
        user_type = "student"
    
    for user in user_list:
        if user["fname"] == fname and user["lname"] == lname:
                return user
        
    return f"{fname} {lname} has not yet been registered as a {user_type}."
        
        

#print(user_search_by_name("Jane", "Doe", teacher_list))

def user_search_by_id(id, user_list):
    '''Searches for user by id in given list.'''
    for user in user_list:        
        if int(user["id"]) == id:
            return user


################################################# PEP-8, Add logic to print student info; then use some of code to display student and teacher's own info??
def view_users_info(user):
    '''Displays teacher or student information.'''
    # If user is a teacher, find assigned students.
    if "teacher" in user["login_email"]:
        user_type = "teacher"    
        assigned_students_data = []     
         # Iterate through student_ids list, inputting each student id to retrieve their info.     
        i = 0
        while i < len(user["student_ids"]):
            student = user_search_by_id(user["student_ids"][i], student_list) 
                 
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
        for teacher in teacher_list:
            if user["assigned_teacher_id"] == teacher["id"]:
                assigned_teacher = teacher
                break
    
        return f"\n*****{user_type} info*****\n\nName: {user['fname']} {user['lname']}\nID: {user['id']}\nEmail: {user['login_email']}\nSubject: {user['subject']}\nActive lesson ID: {user['current_lesson_id']}\n\n***Assigned teacher***\nName: {teacher['fname']} {teacher['lname']}\nSubject: {teacher['subject']}\nEmail: {teacher['login_email']}\n"

    else:
        return "This user has not yet been registered as a teacher or student."
        
#print(view_users_info((user_search_by_name("Jane", "Doe", teacher_list))))
#print(user_search_by_id(2, teacher_list))
#print(view_users_info((user_search_by_name("David", "Bowie", student_list))))
'''{
        "login_email": "teacher3@school.co.uk",
        "hashed_password": "hsiohji9",
        "id": 3,
        "fname": "Graham",
        "lname": "Student",
        "DOB": "11.02.85",
        "subject": "Science",
        "current_lesson_id": 1,
        "student_ids": [ 904 ]
    },'''

'''login_email": "student6@school.co.uk",
        "hashed_password": "hsiohji9",
        "id": 905,
        "fname": "David",
        "lname": "Bowie",
        "DOB": "11.10,95",
        "subject": "Computer Science",
        "current_lesson_id": 4,
        "assigned_teacher_id: 4'''