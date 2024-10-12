def format_lesson_output(self, empty_list, lesson_list):
        '''Used in multiple methods to display lesson info appropriately.'''

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
        
        return lesson_info_to_return

#### Methods called by teachers and students #########
    def view_all_my_lessons(self):                
        
        lesson_info_to_return = []
        print(self.subject)
        for lesson in self.lessons:
            if lesson["subject"].lower() == self.subject.lower():
                self.format_lesson_output(lesson_info_to_return, lesson)
        
        info_str = "\n".join(lesson_info_to_return)

        return print(info_str)
