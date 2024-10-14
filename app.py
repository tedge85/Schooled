import json
import os
import base64
from cryptography.fernet import Fernet
from requests import delete
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
 
app = Flask(__name__)
api = Api(app)

KEY = os.environ.get("ENCRYPTION_KEY")
FERNET = Fernet(KEY.encode())

def load_list(list_name):
    '''Loads json files - for users or lessons - into dictionaries.'''
    try:
        with open(f"{list_name}.json", "r") as f:
            return json.load(f)
    # create an empty list if list.json has not yet been created.
    except FileNotFoundError:
        return []   

def save_list(user_or_lesson, list_name):
    '''Saves user or lesson dictionaries into json files.'''

    with open(f"{user_or_lesson}.json", "w") as f:
        json.dump(list_name, f, indent=4)

# Initiate list variables by loading from json files        
admin_list = load_list("admin_list")
teacher_list = load_list("teacher_list")
student_list = load_list("student_list")
lesson_list = load_list("lesson_list")

# Lists stored in user_lists to allow for dynamic access e.g. 'if user_list
# in user_lists:...'
user_lists = {
    "student_list": student_list,
    "teacher_list": teacher_list,
    "admin_list": admin_list,
    "lesson_list": lesson_list
}

################ API endpoints. #####################
class Users(Resource):
    
    def get(self, user_list):
        '''Retrieves one of the lists from user_lists, dependeing on input'''    

        if user_list in user_lists:
            return user_lists[user_list], 200                        
        return f"{user_list} not found", 404

class Admin(Resource):
    
    def get(self, email):               
        '''Retrieves admin_list'''
        admin_list = load_list("admin_list")

        for admin in admin_list:
            if email == admin["login_email"]:
                
                return admin, 200        
            
        return "User not found", 404


    def post(self, email):        
        '''Adds a student to student_list.'''
        
        student_list = load_list("student_list")
        
        parser = reqparse.RequestParser()
        parser.add_argument("hashed_password")
        parser.add_argument("id", type=int)
        parser.add_argument("fname")
        parser.add_argument("lname")                
        parser.add_argument("DOB")
        parser.add_argument("subject")
        parser.add_argument("current_lesson_id", type=int)
        parser.add_argument("assigned_teacher_id", type=int) 
         
        args = parser.parse_args()
                                               
        student = {
                "login_email": email,                  
                "hashed_password": args["hashed_password"],
                "id": (args["id"]),
                "fname": args["fname"],
                "lname": args["lname"],
                "DOB": args["DOB"],
                "subject": args["subject"],                
                "current_lesson_id": args["current_lesson_id"],
                "assigned_teacher_id": args["assigned_teacher_id"]
                }

        for s in student_list:
            if s["fname"] == args["fname"] and s["lname"] == args["lname"]:
                return f"User with name '{args['fname']} {args['lname']}' "
                f"already exists", 400                                               
                        
        student_list.append(student)
        
        save_list("student_list", student_list)                        
            
        return student, 201
    

    def delete(self, email):
        '''Removes given student from student_list.'''
        
        student_list = load_list("student_list")

        initial_list_size = len(student_list)

        student_list = [student for student in student_list 
                        if student["login_email"] != email]
                    
        
        if len(student_list) < initial_list_size:
            
            save_list("student_list", student_list)                                 
            
            return "\n**Student deleted**\n", 200
        
        else:
            
            return "!!Student not found!!", 404
            

class SecureAdmin(Resource):
    '''Data sent here is encrypted.'''


    def post(self, email):
        '''Securely adds a student to student_list.'''
        
        student_list = load_list("student_list")

        encrypted_data = request.data
       
        decrypted_data = FERNET.decrypt(encrypted_data).decode("utf-8")
        data = json.loads(decrypted_data) 

        student = {
            "login_email": email,                  
            "hashed_password": data.get("hashed_password"),
            "id": data.get("id"),
            "fname": data.get("fname"),
            "lname": data.get("lname"),
            "DOB": data.get("DOB"),
            "subject": data.get("subject"),                
            "current_lesson_id": data.get("current_lesson_id"),
            "assigned_teacher_id": data.get("assigned_teacher_id")
         }

        for s in student_list:
            s_fname = s["fname"].lower()
            s_lname = s["lname"].lower()
            fname_input = data.get("fname").lower()
            lname_input = data.get("lname").lower()
            
            if s_fname ==  fname_input and s_lname == lname_input:
                return f"User with name '{data.get('fname')} "
                f"{data.get('lname')}' already exists", 400                                               
                        
        student_list.append(student)
        
        save_list("student_list", student_list)                      
            
        return student, 201

class Teacher(Resource):    
    
    def get(self, email):
        '''Retrieves single teacher data from teacher_list.'''
        
        teacher_list = load_list("teacher_list")

        for teacher in teacher_list:
            if email == teacher["login_email"]:
                
                return teacher, 200
            else:
                continue
            
        return "User not found", 404        
    
    def patch(self, email):                
        '''Allows student ids to be assigned to teachers.'''
        
        teacher_list = load_list("teacher_list")

        parser = reqparse.RequestParser()        
        parser.add_argument("student_id", type=int)
        parser.add_argument("assigned_teacher_id", type=int)        
         
        args = parser.parse_args()

        
        original_list_len = 0
        amended_list_len = 0 # Initialised with low value so that defaults 
                             # to not meet below condition if something goes 
                             # wrong. 
        
        for teacher in teacher_list:
            if int(teacher["id"]) == args["assigned_teacher_id"]:
                
                original_list_len = len(teacher["student_ids"])                        
                
                teacher["student_ids"].append(args["student_id"])

                amended_list_len = len(teacher["student_ids"])        
                
        if original_list_len < amended_list_len:
            
            save_list("teacher_list", teacher_list)                        
            
            return "**List amended**", 200
        
        else:
            return "Teacher not found", 404

        
class SecureTeacher(Resource):
    '''Securely allows student ids to be assigned to teachers.'''
    
    def patch(self, email):
        
        teacher_list = load_list("teacher_list")

        encrypted_data = request.data
       
        decrypted_data = FERNET.decrypt(encrypted_data).decode("utf-8")
        data = json.loads(decrypted_data)
        
        original_list_len = 0
        amended_list_len = 0 # Initialised with low value so that defaults to 
                             # not meet below condition if something goes 
                             # wrong. 
        
        for teacher in teacher_list:
            if int(teacher["id"]) == data.get("assigned_teacher_id"):
                
                original_list_len = len(teacher("student_ids"))                        
                
                teacher["student_ids"].append(data.get("student_id"))

                amended_list_len = len(teacher["student_ids"])        
                
        if original_list_len < amended_list_len:
            
            save_list("teacher_list", teacher_list)                        
            
            return "**List amended**", 200
        
        else:
            
            return "Teacher not found", 404
        

class AssignedStudent(Resource): 
    
    def get(self, teacher_id):        
        '''Retrieves students assigned to given teachers.'''
        
        student_list = load_list("student_list")

        student_names = []
        for student in student_list:
            
             if teacher_id == int(student["assigned_teacher_id"]):
                student_names.append(f"\n{student['fname']} {student['lname']}"
                                     f"\nActive lesson ID:" 
                                     f"{student['current_lesson_id']}\nEmail: "
                                     f"{student['login_email']}\n_____________"
                                     "_________")
                
        if student_names:
            return student_names   
        return "User not found", 404                
    

class Student(Resource):
    
    def get(self, email):
        '''Retrieves single student information.'''
        
        student_list = load_list("student_list")

        for student in student_list:
            if email == student["login_email"]:
                
                return student, 200
            else:
                continue
            
        return "User not found", 404                                                          
        

class AssignedTeacher(Resource): # change to input just student id?
    
     def get(self, student_id):        
        '''Retrieves students' assigned teachers from teacher_list.'''      
        
        teacher_list = load_list("teacher_list")
        
        for teacher in teacher_list:
            #for num in teacher["ids"]:                          
             if int(student_id) in teacher["student_ids"]:
                return teacher, 200
                continue
        return "User not found", 404         
     
     def patch(self, student_id):
        '''Removes a deleted student's id from teacher['student_ids']'''                                     
        
        teacher_list = load_list("teacher_list")
        
        original_list_len = 0
        amended_list_len = 0
        
        for teacher in teacher_list:
            
            if student_id in teacher["student_ids"]:
                original_list_len = len(teacher["student_ids"])
                teacher["student_ids"] = [id_value for id_value in 
                                          teacher["student_ids"] if 
                                          id_value != student_id]
                amended_list_len = len(teacher["student_ids"])
                continue
        
        save_list("teacher_list", teacher_list)                

        if original_list_len > amended_list_len:
            return "\n***ID deleted***\n", 200
        
        else:
            return "User not found", 404
        
          
class Lesson(Resource):
    
    def get(self, subject):
        '''Retrieves single lessons.'''
        
        lesson_list = load_list("lesson_list")
        

        if lesson_list:
            return lesson_list, 201
        
        else:
            return "Lessons not found", 404

    def post(self, subject):
        '''Posts new lessons to lesson_list.'''
        
        lesson_list = load_list("lesson_list")

        parser = reqparse.RequestParser()
        parser.add_argument("lesson_id", type=int)
        parser.add_argument("title", type=str)
        parser.add_argument("input", type=str)
        parser.add_argument("question_1", type=str)
        parser.add_argument("question_2", type=str)
        parser.add_argument("question_3", type=str)
        parser.add_argument("question_4", type=str)
        parser.add_argument("question_5", type=str)
        parser.add_argument("answer_1", type=str)
        parser.add_argument("answer_2", type=str)
        parser.add_argument("answer_3", type=str)
        parser.add_argument("answer_4", type=str)
        parser.add_argument("answer_5", type=str)
        parser.add_argument("grade", type=str)
        args = parser.parse_args()
        
        lesson = {
                "lesson_id": args["lesson_id"],
                "subject": subject,
                "title": args["title"],
                "input": args["input"],
                "questions": [args["question_1"],args["question_2"], 
                              args["question_3"], args["question_4"], 
                              args["question_5"]],
                "answers": [args["answer_1"], args["answer_2"], 
                            args["answer_3"], args["answer_4"], 
                            args["answer_5"]],
                "grade": args["grade"]
                }
        
        lesson_list.append(lesson)        

        save_list("lesson_list", lesson_list)                

        return lesson, 201
    

    def patch(self, subject):     
        '''Updates lesson content in lesson_list.'''

        lesson_list = load_list("lesson_list")
        
        parser = reqparse.RequestParser()        
        parser.add_argument("lesson_id", type=int)
        parser.add_argument("title", type=str)
        parser.add_argument("input", type=str)
        parser.add_argument("question_1", type=str)
        parser.add_argument("question_2", type=str)
        parser.add_argument("question_3", type=str)
        parser.add_argument("question_4", type=str)
        parser.add_argument("question_5", type=str)
        parser.add_argument("answer_1", type=str)
        parser.add_argument("answer_2", type=str)
        parser.add_argument("answer_3", type=str)
        parser.add_argument("answer_4", type=str)
        parser.add_argument("answer_5", type=str)
        parser.add_argument("grade", type=str)
    
        args = parser.parse_args()                
 
        for lesson in lesson_list:
            l_subject = str(lesson["subject"]).lower()
            l_id = lesson["lesson_id"]
            if l_subject == str(subject).lower() and l_id == args["lesson_id"]:                
         
                # Don't change automatically assigned lesson ID and subject.
                lesson["lesson_id"] = lesson["lesson_id"] 
                lesson["subject"] = lesson["subject"]
         
                # Conditions set to change values if keyword arguments provided
                # otherwise keep them the same.                                
                if args["title"] != None:                    
                    lesson["title"] = args["title"]
                else:
                    lesson["title"] = lesson["title"]
         
                if args["question_1"] != "":
                    lesson["questions"][0] = args["question_1"]                        
                else:
                    lesson["questions"] = lesson["questions"]
             
                if args["question_2"] != "":
                    lesson["questions"][1] = args["question_2"]                        
                else:
                    lesson["questions"] = lesson["questions"]
         
                if args["question_3"] != "":
                    lesson["questions"][2] = args["question_3"]                        
                else:
                    lesson["questions"] = lesson["questions"]
             
                if args["question_4"] != "":
                    lesson["questions"][3] = args["question_4"]                        
                else:
                    lesson["questions"] = lesson["questions"]
                         
                if args["question_5"] != "":
                    lesson["questions"][4] = args["question_5"]                        
                else:
                    lesson["questions"] = lesson["questions"]

                if args["answer_1"] != "":
                    lesson["answers"][0] = args["answer_1"]                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if args["answer_2"] != "":
                    lesson["answers"][1] = args["answer_2"]                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if args["answer_3"] != "":
                    lesson["answers"][2] = args["answer_3"]                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if args["answer_4"] != "":
                    lesson["answers"][3] = args["answer_4"]                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if args["answer_5"] != "":
                    lesson["answers"][4] = args["answer_5"]                        
                else:
                    lesson["answers"] = lesson["answers"]
                                                                         
                if args["grade"] != None:
                   lesson["grade"] = args["grade"]
            
                else:
                    lesson["grade"] = lesson["grade"]                                           
                                                                                   
        save_list("lesson_list", lesson_list)
                                 
        return lesson, 200
                                
                              
class SecureLesson(Resource):
    '''Data sent here is encrypted.'''
    
    def post(self, subject):
        '''Securely posts new lessons to lesson_list.'''
        
        lesson_list = load_list("lesson_list")

        encrypted_data = request.data
       
        decrypted_data = FERNET.decrypt(encrypted_data).decode("utf-8")
        data = json.loads(decrypted_data)               
                
        lesson = {
                "lesson_id": data.get("lesson_id"),
                "subject": subject,
                "title": data.get("title"),
                "input": data.get("input"),
                "questions": [data.get("question_1"), data.get("question_2"),
                              data.get("question_3"), data.get("question_4"), 
                              data.get("question_5")],
                "answers": [data.get("answer_1"), data.get("answer_2"), 
                            data.get("answer_3"), data.get("answer_4"), 
                            data.get("answer_5")],
                "grade": data.get("grade")
                }
        
        lesson_list.append(lesson)        

        save_list("lesson_list", lesson_list)            

        return lesson, 201


    def patch(self, subject):
        '''Securely updates lesson content in lesson_list.'''
        
        lesson_list = load_list("lesson_list")

        encrypted_data = request.data
       
        decrypted_data = FERNET.decrypt(encrypted_data).decode("utf-8")
        data = json.loads(decrypted_data)               

        for lesson in lesson_list:
            
            if lesson["subject"] == subject:
                
                # Don't change automatically assigned lesson ID and subject.
                lesson["lesson_id"] = lesson["lesson_id"] 
                lesson["subject"] = lesson["subject"]
         
                # Conditions set to change values if keyword arguments provided
                # otherwise keep them the same.                                
                if data.get("title") != None:                    
                    lesson["title"] = data.get("title")
                else:
                    lesson["title"] = lesson["title"]
         
                if data.get("question_1") != "":
                    lesson["questions"][0] = data.get("question_1")                        
                else:
                    lesson["questions"] = lesson["questions"]
             
                if data.get("question_2") != "":
                    lesson["questions"][1] = data.get("question_1")                        
                else:
                    lesson["questions"] = lesson["questions"]
         
                if data.get("question_3") != "":
                    lesson["questions"][2] = data.get("question_3")                        
                else:
                    lesson["questions"] = lesson["questions"]
             
                if data.get("question_4") != "":
                    lesson["questions"][3] = data.get("question_4")                        
                else:
                    lesson["questions"] = lesson["questions"]
                         
                if data.get("question_5") != "":
                    lesson["questions"][4] = data.get("question_5")                        
                else:
                    lesson["questions"] = lesson["questions"]

                if data.get("answer_1") != "":
                    lesson["answers"][0] = data.get("answer_1")                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if data.get("answer_2") != "":
                    lesson["answers"][1] = data.get("answer_2")                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if data.get("answer_3") != "":
                    lesson["answers"][2] = data.get("answer_3")                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if data.get("answer_4") != "":
                    lesson["answers"][3] = data.get("answer_4")                        
                else:
                    lesson["answers"] = lesson["answers"]
             
                if data.get("answer_5") != "":
                    lesson["answers"][4] = data.get("answer_5")                        
                else:
                    lesson["answers"] = lesson["answers"]
                                                                         
                if data.get("grade") != None:
                    lesson["grade"] = data.get("grade")
            
                else:
                    lesson["grade"] = lesson["grade"]                                                    
                     
        save_list("lesson_list", lesson_list)
                                              
        return lesson, 200                
                
                
api.add_resource(Users, "/<string:user_list>")
api.add_resource(Admin, "/users/admins/<string:email>") 
api.add_resource(SecureAdmin, "/users/secure/admins/<string:email>")
api.add_resource(Teacher, "/users/teachers/<string:email>")
api.add_resource(SecureTeacher, "/users/secure/teachers/<string:email>")
api.add_resource(AssignedStudent, "/users/teachers/assignedstudent/"
                                                 "<int:teacher_id>")
api.add_resource(Student, "/users/students/<string:email>")
api.add_resource(AssignedTeacher, "/users/students/assignedteacher/"
                                                 "<int:student_id>")
api.add_resource(Lesson, "/lessons/<subject>")
api.add_resource(SecureLesson, "/lessons/secure/<subject>")

app.run(debug=True)
