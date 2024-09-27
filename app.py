###TO DO####
# Add subject_taught key to teacher_list, corresponding to subject_studied key to student_list
# Make lesson dictionary.
# Make admin dictionary
# Make sure new keys marry up to arguments passed

import json
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
 
app = Flask(__name__)
api = Api(app)

# Functions that load dictionaries from json files.
def load_admin_list():
    try:
        with open("admin_list.json", "r") as f:
            return json.load(f)
    # create an empty list if admin_list.json has not yet been created.
    except FileNotFoundError:
        return []

def load_teacher_list():
    try:
        with open("teacher_list.json", "r") as f:
            return json.load(f)
    # create an empty list if teacher_list.json has not yet been created.
    except FileNotFoundError:
        return []
    
def load_student_list():
    try:
        with open("student_list.json", "r") as f:
            return json.load(f)
    # create an empty list if student_list.json has not yet been created.
    except FileNotFoundError:
        return []
    
# Functions that save dictionaries to json files.
def save_admin_list():
    with open("admin_list.json", "w") as f:
        json.dump(teacher_list, f, indent=4)        

def save_teacher_list():
    with open("teacher_list.json", "w") as f:
        json.dump(teacher_list, f, indent=4)
        
def save_student_list():
    with open("student_list.json", "w") as f:
        json.dump(student_list, f, indent=4)
        
admin_list = load_admin_list()
teacher_list = load_teacher_list()
student_list = load_student_list()

user_lists = {
    "student_list": student_list,
    "teacher_list": teacher_list
}


# API endpoints.
class Users(Resource):
    def get(self, user_list):        
        if user_list in user_lists:
            return user_lists[user_list], 200                        
        return f"{user_list} not found", 404



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

        for student in student_list:
            #for num in teacher["ids"]:                          
             if id in student["id"]:
                    return student, 200
                    continue
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
    
     def get(self, id):        
        id = int(id)

        for teacher in teacher_list:
            #for num in teacher["ids"]:                          
             if id in teacher["ids"]:
                    return teacher, 200
                    continue
        return "User not found", 404    

class Admin(Resource):
    
    def post(self, teacher_lname=None, student_lname=None):
        
        parser = reqparse.RequestParser()        
        parser.add_argument("fname")
        parser.add_argument("login_email")
        parser.add_argument("hashed_password")        
        parser.add_argument("DOB")
        parser.add_argument("lesson_id") # Change class method to match subject input to lesson_id
         
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
                "lesson_id": args["lesson_id"],
                "ids": []
            }
            teacher_list.append(teacher)
            save_teacher_list()
            return teacher, 201
    
        else:
            student = {
                "login_email": args["login_email"],                  
                "hashed_password": args["hashed_password"],
                "id": args["id"],
                "fname": args["fname"],
                "lname": teacher_lname,
                "DOB": args["DOB"],
                "lesson_id": args["lesson_id"],
                "id": None # Change logic on class method/cli to assign according to lesson choice. Then assign to teacher
            }
                        
            student_list.append(teacher)
            save_student_list()
            return student, 201
        
api.add_resource(Users, "/<string:user_list>")
api.add_resource(Admin, "/users/register/<string:lname>")
api.add_resource(Teacher, "/users/teachers/<string:email>")
api.add_resource(AssignedStudent, "/users/teachers/<int:id>/assignedstudent")
api.add_resource(Student, "/users/students/<string:email>")
api.add_resource(AssignedTeacher, "/users/students/<int:id>/assignedteacher")

 
app.run(debug=True)




