import requests

API_URL = "http://127.0.0.1:5000"

######## Test all of these lesson methods
############################################ return code from json then have lessons_list only return json object if response is not 404!
######## Figure out how to add first new lesson!!!

#subject_list_path = requests.get(f"{API_URL}/lessons/English", headers={"Content-Type": "application/json"})

#if subject_list_path.status_code != 404:
 #   lessons = subject_list_path.json()
       

def change_lesson_content(subject, lesson_id, title=None, lesson_input=None, questions=[], answers=[], grade=None):
        
        '''Modifies lesson data.'''
        new_lesson_data = {
            "lesson_id": lesson_id,
            "subject": subject,        
            "title": title,
            "input": lesson_input,
            "questions": [questions],
            "answers": [answers],                        
            "grade": grade    
         }
        headers = {"Content-Type": "application/json"}  
        response = requests.patch(f"{API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
        if response.status_code == 201:
        
            return(response.json())
        
        return("Oops! Something went wrong.")

'''def return_active_lesson_id(self, subject):
        
        latest_lesson_id = 0
        
        for lesson in self.lessons:
            if lesson["subject"].lower() == subject.lower():                
                if int(lesson["lesson_id"]) > latest_lesson_id:
                    latest_lesson_id = lesson["lesson_id"]
            else:
                return 0 
        
        return latest_lesson_id'''

 #print(change_lesson_content("English", 1, title="BLAMMO", answers=["Five", "yes", "dunno", "huh?", "Panama?"]))
def format_lesson_output(empty_list, lesson_list):            
        lesson_ID = lesson_list["lesson_id"]
        subject = lesson_list["subject"]
        title = lesson_list["title"]
        lesson_input = lesson_list["input"]
        i = 0
        q_num = 1
        question_str = ""
        while i < len(lesson_list["questions"]):
            question_str += f"\n{q_num}){lesson_list['questions'][i]}\n"
            i += 1
            q_num += 1
        j = 0
        a_num = 1
        answer_str = ""   
        while j < len(lesson_list["answers"]):
            answer_str + f"\n{a_num}){lesson_list['answers'][j]}\n"
            j += 1
            q_num += 1
        
        grade = lesson_list["grade"]    
    
        info = f"\nLesson ID: {lesson_ID}\nSubject: {subject}\nTitle: {title}\nInput: {lesson_input}\nQuestions: \n{question_str}\nAnswers: \n{answer_str}\nGrade: {grade}"
    
        lesson_info_to_return = empty_list.append(info)
        
        return print(lesson_info_to_return)
    
   ''' #### Method called by admin only
def view_all_lessons():
            
        lesson_info_to_return = []
    
        for lesson in lessons:
            format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return info_str
    
    
    #### Methods called by teachers and students #########
def view_all_my_lessons(subject):                
        
        lesson_info_to_return = []

        for lesson in lessons:
            if lesson["subject"].lower() == subject.lower():
                format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return info_str

def view_my_active_lesson(subject, current_lesson_id):            
        
        lesson_info_to_return = []

        for lesson in lessons:            
            if lesson["subject"].lower() == subject.lower() and int(current_lesson_id) == int(lesson["lesson_id"]):
                format_lesson_output(lesson_info_to_return, lesson)
            
        info_str = "\n".join(lesson_info_to_return) 
        return info_str'''
        



#current_lesson_id = int(return_active_lesson_id("Computer Science"))
#new_lesson_id = int(current_lesson_id) + 1

'''def add_new_lesson(subject, title, lesson_input, questions=[], answers=[], grade=None, lesson_id=new_lesson_id):
        #Adds a new lesson, automatically assigning lesson id.
        new_lesson_data = {
            "lesson_id": (new_lesson_id),
            "subject": subject,
            "title": title,
            "input": lesson_input,
            "questions": [questions],        
            "answers": [answers],
            "grade": "None"
        }
        headers = {"Content-Type": "application/json"}  
        response = requests.post(f"{API_URL}/lessons/{subject}", headers=headers, json=new_lesson_data)
        if response.status_code == 201:
            lesson_info_to_return = []
            format_lesson_output(lesson_info_to_return, new_lesson_data)
            info_str = "\n".join(lesson_info_to_return) 
            return info_str
     
        return("Oops! Something went wrong.")'''


#print(add_new_lesson("Computer Science", "logical operators", "Some input", questions=["What is the outcome: 1 AND 1?", "What is the outcome: 0 AND 0?", "What is the outcome: 1 OR 1?", "What is the outcome:1 XOR 1?", "What is the outcome: 1 XOR 0)?"]))


