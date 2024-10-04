import requests

API_URL = "http://127.0.0.1:5000"

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
    #if response.status_code == 201:
        
    return(response.json())
     

    return("Oops! Something went wrong.")

print(add_lesson_answers("English", 1, title="Eng", question_1="Test", question_2="where", 
                       question_3="anything", question_4=None, question_5=None, answer_1="test1", 
                       answer_2="test2", answer_3="test3", answer_4="test4", answer_5="test5", grade="A"))
