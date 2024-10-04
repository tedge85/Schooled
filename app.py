###TO DO####
# Add subject_taught key to teacher_list, corresponding to subject_studied key to student_list
# Make lesson json file. /
# Make admin json file. /
# Make dynamic load and save file method /
# Make sure new keys marry up to arguments passed
# Use tuples - FOR IDS?
# Check codes correct

###### Think again about lesson list ids - id for subject

######SECURITY TO IMPLEMENT#####
# Logging events??
# Obfuscate sensitive data in URIs - base64.
# password attempt limiter
# HTTPS

import json
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
 
app = Flask(__name__)
api = Api(app)

def load_list(list_name):
    '''Loads json files - for users or lessons - into dictionaries.'''
    try:
        with open(f"{list_name}", "r") as f:
            return json.load(f)
    # create an empty list if list.json has not yet been created.
    except FileNotFoundError:
        return []   

def save_list(user_or_lesson, list_name):
    '''Saves user or lesson dictionaries into json files.'''

    with open(f"{user_or_lesson}_list.json", "w") as f:
        json.dump(list_name, f, indent=4)
        
admin_list = load_list("admin_list.json")
teacher_list = load_list("teacher_list.json")
student_list = load_list("student_list.json")
lesson_list = load_list("lesson_list.json")


user_lists = {
    "student_list": student_list,
    "teacher_list": teacher_list
}

################ API endpoints. #####################
class Users(Resource):
    def get(self, user_list):        
        if user_list in user_lists:
            return user_lists[user_list], 200                        
        return f"{user_list} not found", 404

class Admin(Resource):
    pass

class Teacher(Resource):
    
    def get(self, email):
        
        for teacher in teacher_list:
            if email == teacher["login_email"]:
                
                return teacher, 200
            else:
                continue
            
        return "User not found", 404        

class AssignedStudent(Resource): 
    
     def get(self, id):        
        id = int(id)
        
        student_names = []
        for student in student_list:
            
             if id == int(student["assigned_teacher_id"]):
                student_names.append(f"{student['fname']} {student['lname']}")
                
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
        
    
        
        
        
    def put(self, name, users): ###################################
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()
 
        for user in users:
            if(name == user["name"]):
                user["age"] = args["age"]
                user["occupation"] = args["occupation"]
                return user, 200
        
        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201
 
    def delete(self, name): #####################################
        global users
        users = [user for user in users if user["name"] != name]
        return "{} is deleted.".format(name), 200


class AssignedTeacher(Resource): # change to input just student id?
    
     def get(self, student_id):        
         

        for teacher in teacher_list:
            #for num in teacher["ids"]:                          
             if int(student_id) in teacher["student_ids"]:
                return teacher, 200
                continue
        return "User not found", 404    

class Admin(Resource):
    
    def get(self, email):                
        
        if email == admin_list["login_email"]:
                
            return admin_list, 200        
            
        return "User not found", 404

    def post(self, teacher_lname=None, student_lname=None):
        
        parser = reqparse.RequestParser()        
        parser.add_argument("fname")
        parser.add_argument("login_email")
        parser.add_argument("hashed_password")        
        parser.add_argument("DOB")
        parser.add_argument("current_lesson_id") # Change class method to match subject input to current_lesson_id
         
        args = parser.parse_args()
        
        if teacher_lname:
            for t in teacher_list:
                if(args["fname"] == t["fname"]) and (teacher_lname == t["lname"]):
                    return f"User with name '{args['fname']} {teacher_lname}' already exists", 400
                
        elif student_lname:
            for s in student_list:
                if(args["fname"] == s["fname"]) and (student_lname == s["lname"]):
                    return f"User with name '{args['fname']} {student_lname}' already exists", 400
        
        if teacher_lname:
            
            # Find what the last id assigned was and add 1 to this to generate new id.
            last_id = 0
            for t in teacher_list:
                if t["id"] > last_id:
                    last_id = t["id"]                    
                    continue
            
            next_id = last_id + 1

            teacher = {
                "login_email": args["login_email"],                  
                "hashed_password": args["hashed_password"],
                "id": next_id,
                "fname": args["fname"],
                "lname": teacher_lname,
                "DOB": args["DOB"],
                "current_lesson_id": args["current_lesson_id"],
                "ids": []
            }
            teacher_list.append(teacher)
            save_list("teacher", teacher_list)
            return teacher, 201
    
        else:
            student = {
                "login_email": args["login_email"],                  
                "hashed_password": args["hashed_password"],
                "id": args["id"],
                "fname": args["fname"],
                "lname": teacher_lname,
                "DOB": args["DOB"],
                "current_lesson_id": args["current_lesson_id"],
                "id": None # Change logic on class method/cli to assign according to lesson choice. Then assign to teacher
            }
                        
            student_list.append(teacher)
            save_list("student", student_list)
            return student, 201
        
class Lessons(Resource):
    def get(self):               
        return lesson_list
        return "User not found", 404    

class Lesson(Resource):
    def get(self):
        return lesson_list, 201

    def post(self, subject):
        
        parser = reqparse.RequestParser()
        parser.add_argument("lesson_id")
        parser.add_argument("title")
        parser.add_argument("input")
        parser.add_argument("questions")
        parser.add_argument("answers")
        parser.add_argument("grade")
        args = parser.parse_args()
        
        lesson = {
                "lesson_id": args["lesson_id"],
                "subject": subject,
                "title": args["title"],
                "input": args["input"],
                "questions": args["questions"],
                "answers": args["answers"],
                "grade": args["grade"]
                }
        
        lesson_list.append(lesson)
        

        save_list("lesson", lesson_list)

        return lesson, 201
    
    def patch(self, subject):        
        
        parser = reqparse.RequestParser()
        parser.add_argument("lesson_id")
        parser.add_argument("title")
        parser.add_argument("question_1")
        parser.add_argument("question_2")
        parser.add_argument("question_3")
        parser.add_argument("question_4")
        parser.add_argument("question_5")
        parser.add_argument("answer_1", type=str)
        parser.add_argument("answer_2", type=str)
        parser.add_argument("answer_3", type=str)
        parser.add_argument("answer_4", type=str)
        parser.add_argument("answer_5", type=str)
        parser.add_argument("grade", type=str)
        
        args = parser.parse_args()
        
        for lesson in lesson_list:
            if subject == lesson["subject"]: #and args["lesson_id"] == lesson["lesson_id"]:
                
                lesson["lesson_id"] = lesson["lesson_id"]
                lesson["subject"] = lesson["subject"]
                lesson["title"] = args["title"]
                lesson["question_1"] = args["question_1"]
                lesson["question_2"] = lesson["question_2"]
                lesson["question_3"] = lesson["question_3"]
                lesson["question_4"] = lesson["question_4"]
                lesson["question_5"] = lesson["question_5"]
                lesson["answer_1"] = str(args["answer_1"])
                lesson["answer_2"] = args["answer_2"]
                lesson["answer_3"] = args["answer_3"]
                lesson["answer_4"] = args["answer_4"]           
                lesson["answer_5"] = args["answer_5"]                                
                lesson["grade"] = args["grade"]

                
            save_list("lesson", lesson_list)
            return lesson, 201
        return lesson_list #"lesson not found", 404
                             

        '''if args["title"]:
                    lesson["title"] = args["title"]
                if args["input"]:
                    lesson["input"] = args["input"]
                if args["question_1"]:
                    lesson["questions"]["1"] = args["question_1"]
                if args["answer_1"]:
                    lesson["answers"]["1"] = args["answer_1"]
                if args["answer_2"]:
                    lesson["answers"]["2"] = args["answer_2"]
                if args["answer_3"]:
                    lesson["answers"]["3"] = args["answer_3"]
                if args["answer_4"]:
                    lesson["answers"]["4"] = args["answer_4"]
                if args["answer_5"]:
                    lesson["answers"]["5"] = args["answer_5"]
                if args["grade"]:
                    lesson["grade"] = args["grade"]''' 

class MathsLessons(Resource):
    pass

class ScienceLessons(Resource):
    pass

class ComputerScienceLessons(Resource):
    pass

api.add_resource(Users, "/<string:user_list>")
#api.add_resource(Admin, "/users/admins/<string:lname>")
api.add_resource(Teacher, "/users/teachers/<string:email>")
api.add_resource(AssignedStudent, "/users/teachers/<int:id>/assignedstudent")
api.add_resource(Student, "/users/students/<string:email>")
api.add_resource(AssignedTeacher, "/users/students/<int:student_id>/assignedteacher")

api.add_resource(Admin, "/users/admins/<string:email>") 

api.add_resource(Lessons, "/lessons")
api.add_resource(Lesson, "/lessons/<string:subject>")
api.add_resource(MathsLessons, "/maths/<int:lesson_id>")
api.add_resource(ScienceLessons, "/science/<int:lesson_id>")
api.add_resource(ComputerScienceLessons, "/Computer Science/<int:lesson_id>")
app.run(debug=True)




