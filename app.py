import json

from requests import delete
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
 
app = Flask(__name__)
api = Api(app)

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
        
admin_list = load_list("admin_list")
teacher_list = load_list("teacher_list")
student_list = load_list("student_list")
lesson_list = load_list("lesson_list")


user_lists = {
    "student_list": student_list,
    "teacher_list": teacher_list,
    "admin_list": admin_list
}

################ API endpoints. #####################
class Users(Resource):
    def get(self, user_list):        
        if user_list in user_lists:
            return user_lists[user_list], 200                        
        return f"{user_list} not found", 404

class Admin(Resource):
    
    def get(self, email):               
        for admin in admin_list:
            if email == admin["login_email"]:
                
                return admin, 200        
            
        return "User not found", 404


    def post(self, email):
        '''Adds a student to student_list.'''
        
        student_list = user_lists["student_list"]
        
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
                return f"User with name '{args['fname']} {args['lname']}' already exists", 400                                               
                        
        student_list.append(student)
        
        save_list("student_list", student_list)        
        
        student_list = load_list("student_list")
            
        return student, 201
    

    def delete(self, email):
        '''Removes given student from student_list.'''
        
        student_list = user_lists["student_list"]

        initial_list_size = len(student_list)

        student_list = [student for student in student_list if student["login_email"] != email]
                    
        
        if len(student_list) < initial_list_size:
            
            save_list("student_list", student_list)
        
            student_list = load_list("student_list")    
            
            
            return "\n**Student deleted**\n", 200
        
        else:
            
            return "!!Student not found!!", 404
            
        

class Teacher(Resource):
    '''Retrieves single teacher data from teacher_list.'''
    
    def get(self, email):
        
        for teacher in teacher_list:
            if email == teacher["login_email"]:
                
                return teacher, 200
            else:
                continue
            
        return "User not found", 404        
    
    def patch(self, email):                

        parser = reqparse.RequestParser()        
        parser.add_argument("student_id", type=int)
        parser.add_argument("assigned_teacher_id", type=int)        
         
        args = parser.parse_args()

        
        original_list_len = 0
        amended_list_len = 0 # Initialised with low value so that defaults to not meet below condition if something goes wrong. 
        
        for teacher in teacher_list:
            if int(teacher["id"]) == args["assigned_teacher_id"]:
                
                original_list_len = len(teacher["student_ids"])                        
                
                teacher["student_ids"].append(args["student_id"])

                amended_list_len = len(teacher["student_ids"])        
                
        if original_list_len < amended_list_len:
            
            save_list("teacher_list", teacher_list)
            
            teacher_list = load_list("teacher_list", teacher_list)
            
            return "**List amended**", 200
        
        else:
            return "Teacher not found", 404
        

class AssignedStudent(Resource): 
    
    def get(self, teacher_id):        
                
        student_names = []
        for student in student_list:
            
             if teacher_id == int(student["assigned_teacher_id"]):
                student_names.append(f"\n{student['fname']} {student['lname']}\nActive lesson ID: {student['current_lesson_id']}\nEmail: {student['login_email']}________________________")
                
        if student_names:
            return student_names   
        return "User not found", 404                
    

class Student(Resource):
    
    def get(self, email):                
        for student in student_list:
            if email == student["login_email"]:
                
                return student, 200
            else:
                continue
            
        return "User not found", 404                                                 
   
    def post(self, email):
                    
        parser = reqparse.RequestParser()
        parser.add_argument("hashed_password", type=int)
        parser.add_argument("id", type=int)
        parser.add_argument("fname", type=str)
        parser.add_argument("lname", type=str)
        parser.add_argument("dob", type=str)
        parser.add_argument("subject", type=str)
        parser.add_argument("current_lesson_id", type=int)
        parser.add_argument("assigned_teacher_id", type=int)       
        args = parser.parse_args()
        
        original_list_len = len(student_list)

        new_student = {
                "login_email": email,
                "hashed_password": args["hashed_password"],
                "id": args["id"],
                "fname": args["fname"],
                "lname": args["lname"],
                "DOB": args["DOB"],
                "subject": args["subject"],
                "current_lesson_id": args["current_lesson_id"],
                "assigned_teacher_id": args["assigned_teacher_id"]
                }
        
        student_list.append(new_student)
        
        amended_list_len = len(student_list)
        
        save_list("student_list", student_list)
                        
        student_list = load_list("student_list") 

        if original_list_len < amended_list_len:            
            return "***Student enrolled***", 201
        
        else:
            return "Something went wrong", 400        
        

class AssignedTeacher(Resource): # change to input just student id?
    
     def get(self, student_id):        
        '''Retrieves students' assigned teachers from teacher_list.'''      
        for teacher in teacher_list:
            #for num in teacher["ids"]:                          
             if int(student_id) in teacher["student_ids"]:
                return teacher, 200
                continue
        return "User not found", 404         
     
     def patch(self, student_id):
        '''Removes a deleted student's id from teacher['student_ids']'''                                     
        teacher_list = user_lists["teacher_list"]
        
        original_list_len = 0
        amended_list_len = 0
        
        for teacher in teacher_list:
            
            if student_id in teacher["student_ids"]:
                original_list_len = len(teacher["student_ids"])
                teacher["student_ids"] = [id_value for id_value in teacher["student_ids"] if id_value != student_id]
                amended_list_len = len(teacher["student_ids"])
                continue
        
        save_list("teacher_list", teacher_list)
        
        teacher_list = load_list("teacher_list")

        if original_list_len > amended_list_len:
            return "\n***ID deleted***\n", 200
        
        else:
            return "User not found", 404
        
          
class Lesson(Resource):
    def get(self, subject):
        return lesson_list, 201
        return "Lessons not found", 404

    def post(self, subject):
        
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
                "questions": [args["question_1"],args["question_2"], args["question_3"], args["question_4"], args["question_5"]],
                "answers": [args["answer_1"], args["answer_2"], args["answer_3"], args["answer_4"], args["answer_5"]],
                "grade": args["grade"]
                }
        
        lesson_list.append(lesson)        

        save_list("lesson_list", lesson_list)
        
        lesson_list = load_list("lesson_list")

        return lesson, 201
    
    def patch(self, subject):        
        
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
            if str(lesson["subject"]).lower() == str(subject).lower() and (lesson["lesson_id"]) == args["lesson_id"]:                
                
                # Don't change automatically assigned lesson ID and subject.
                lesson["lesson_id"] = lesson["lesson_id"] 
                lesson["subject"] = lesson["subject"]
                
                # Conditions set to change values if keyword arguments provided
                # otherwise keep them the same.
                if args["title"] != None:
                    lesson["title"] = args["title"]
                else:
                    lesson["title"] = lesson["title"]
                
                if args["question_1"] != None:
                    lesson["questions"][0] = args["question_1"]                        
                else:
                    lesson["questions"] = lesson["questions"]
                    
                if args["question_2"] != None:
                    lesson["questions"][1] = args["question_2"]                        
                else:
                    lesson["questions"] = lesson["questions"]
                
                if args["question_3"] != None:
                    lesson["questions"][2] = args["question_3"]                        
                else:
                    lesson["questions"] = lesson["questions"]
                    
                if args["question_4"] != None:
                    lesson["questions"][3] = args["question_4"]                        
                else:
                    lesson["questions"] = lesson["questions"]
                                
                if args["question_5"] != None:
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
                                                                                
                if args["grade"] != "":                    
                    lesson["grade"] = args["grade"]
                else:
                    lesson["grade"] = lesson["grade"]                                           
                            
                save_list("lesson_list", lesson_list)
                return lesson, 201
        
        save_list("lesson_list", lesson_list)
        
        lesson_list = load_list("lesson_list")

        return "lesson not found", 404
                             
        
api.add_resource(Users, "/<string:user_list>")
api.add_resource(Admin, "/users/admins/<string:email>") 
api.add_resource(Teacher, "/users/teachers/<string:email>")
api.add_resource(AssignedStudent, "/users/teachers/assignedstudent/<int:teacher_id>")
api.add_resource(Student, "/users/students/<string:email>")
api.add_resource(AssignedTeacher, "/users/students/assignedteacher/<int:student_id>")
api.add_resource(Lesson, "/lessons/<subject>")
app.run(debug=True)




