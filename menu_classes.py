from ast import Try
import requests
import pwinput

from classes import Admin, Teacher, Student, Lesson, Security

class Menu:
    '''Factory class - children classes inherit options and corresponding 
            methods.'''
            
    def __init__(self, option_1, option_2, method_1, method_2):
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_1 = option_1
        self.option_2 = option_2
                       
        self.method_1 = method_1
        self.method_2 = method_2        

       
class AdminMenu(Menu):
    '''Inherits from Menu and adds extra options and methods.'''

    def __init__(self, option_1, option_2, option_3, option_4, option_5,
                 method_1, method_2, method_3, method_4, method_5):        
        super().__init__(option_1, option_2, method_1, method_2)                                                    
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_3 = option_3
        self.option_4 = option_4
        self.option_5 = option_5
                       
        self.method_3 = method_3
        self.method_4 = method_4        
        self.method_5 = method_5
    
        
    def show_menu(self):
        '''Displays the menu to the users, with options numbers corresponding
           to matching method numbers.''' 
           
        while True:                       
        # presenting the menu to the user and
        # making sure that the user input is converted to lower case.
          print()
          menu = input(f'''Select one of the following Options below:         
                {self.option_1[0].lower()} - {self.option_1}
                {self.option_2[0].lower()} - {self.option_2}
                {self.option_3[0].lower()} - {self.option_3}
                {self.option_4[0].lower()} - {self.option_4}
                {self.option_5[0].lower()} - {self.option_5}      
        :       ''').lower()             
 
          if menu == self.option_1[0].lower():
            self.method_1()               
 
          elif menu == self.option_2[0].lower():
            self.method_2()
          
          elif menu == self.option_3[0].lower():
            self.method_3()               
 
          elif menu == self.option_4[0].lower():
            self.method_4()
            
          elif menu == self.option_5[0].lower():
            self.method_5()
                                    
          else:
            print("\n!! Choose a valid option. !!\n")     
            
class TeacherMenu(AdminMenu):
    '''Inherits from AdminMenu and adds extra options and methods.'''

    def __init__(self, option_1, option_2, option_3, option_4, option_5, 
                 option_6, option_7, method_1, method_2, method_3, method_4,
                 method_5, method_6, method_7):        
        super().__init__(option_1, option_2, option_3, option_4, option_5,
                         method_1, method_2, method_3, method_4, method_5)
        '''Allows for the creation of main menus and sub-menus'''
        
        self.option_6 = option_6
        self.option_7 = option_7
                       
        self.method_6 = method_6
        self.method_7 = method_7        
 
    def show_menu(self):
        '''Displays the menu to the users, with options numbers corresponding
           to matching method numbers.''' 
        
        while True:                       
        # presenting the menu to the user and
        # making sure that the user input is converted to lower case.
          print()
          menu = input(f'''Select one of the following Options below:         
                {self.option_1[0].lower()} - {self.option_1}
                {self.option_2[0].lower()} - {self.option_2}
                {self.option_3[0].lower()} - {self.option_3}
                {self.option_4[0].lower()} - {self.option_4}
                {self.option_5[0].lower()} - {self.option_5}
                {self.option_6[0].lower()} - {self.option_6}
                {self.option_7[0].lower()} - {self.option_7}                
        :       ''').lower()             
 
          if menu == self.option_1[0].lower():
            self.method_1()               
 
          elif menu == self.option_2[0].lower():
            self.method_2()
          
          elif menu == self.option_3[0].lower():
            self.method_3()               
 
          elif menu == self.option_4[0].lower():
            self.method_4()
            
          elif menu == self.option_5[0].lower():
            self.method_5()
            
          elif menu == self.option_6[0].lower():
            self.method_6()
          
          elif menu == self.option_7[0].lower():
            self.method_7()                          
                                    
          else:
            print("\n!! Choose a valid option. !!\n")     

class StudentMenu(AdminMenu):
    '''Inherits from AdminMenu without modifying.'''
    
    def __init__(self, option_1, option_2, option_3, option_4, option_5, 
                 method_1, method_2, method_3, method_4, method_5):        
        
        super().__init__(option_1, option_2, option_3, option_4, option_5,
                         method_1, method_2, method_3, method_4, method_5)

        '''Allows for the creation of main menus and sub-menus'''

class LoginMenu():
    
    API_URL = "http://127.0.0.1:5000"
        
    def __init__(self, security=False, attempts=1):
        
        self.security = security
        self.attempts = attempts        
        
        self.secure_app = Security(self.attempts)
        
        # If security activated by user input, instantiate security object and
        # call method to check login attempts, locking account if more than 4 made.
        if self.security:                                 
            self.secure_app.password_attempts_check()
                                                              
        self.show_menu() # Display the login menu.


    def show_menu(self):
        '''Displays the login menu'''                        

        # If security is currently turned off, give user option to turn it on.
        if self.security == False:
            while True:
                try:
                    choice = input("\n***Type 's' to switch Security on," 
                                   " or press 'c'"
                                   " to continue***: ").lower()
                    if choice == 's':
                       self.security = True
                       break
                    elif choice == 'c':
                        break
                except KeyError:
                    print("Pick a valid choice!")
                
        self.login_email = str(input("\n* Enter your email address: "))
        password = pwinput.pwinput("* Enter your password: ") # Mask password
                                                            # input.
        
        # Hash the password so that it can be compared to the stored hashed 
        # password.
        self.password = self.secure_app.hash_password(str(password))

        # If user identified as admin, API call made to obtain list of admin 
        # users and details.
        if "admin" in str(self.login_email):            
            user_type ="admin"
            
            user_list = requests.get(f"{self.API_URL}/admin_list", 
                        headers={"Content-Type":"application/json"}).json()
        
        # If user identified as teacher, API call made to obtain list of 
        # teacher users and details.
        elif "teacher" in str(self.login_email):            
            user_type ="teacher"
            user_list = requests.get(f"{self.API_URL}/teacher_list",
                        headers={"Content-Type":"application/json"}).json()
        
        # If user identified as teacher, API call made to obtain list of 
        # teacher users and details.
        elif "student" in str(self.login_email):
            user_type ="student"
            user_list = requests.get(f"{self.API_URL}/student_list",
                        headers={"Content-Type": "application/json"}).json()
            
        else:
            print("That email address is not valid.")
            
            # If security is activated, monitor login attempts to later pass
            # to security object and password_attempts_check method to ensure
            # account lockout after 4 attempts.
            
            if self.security:
                self.attempts += 1
                
                # Reset onoce 5 attempts reached, so that counter starts again
                # after lock-out.
                if self.attempts == 5:
                    self.attempts = 1
                    
                new_menu = LoginMenu(security=True, attempts=self.attempts)                

            else:
                new_menu = LoginMenu()
            
                print(f"Login attempts: {self.attempts}")        
                                                    
        # Locate user's login details.
        for user in user_list:            
            login_email = str(user["login_email"])
            password = str(user["hashed_password"]) 
            if login_email == self.login_email and password == self.password:
                
                # Instantiate relevant user object to gain access to its 
                # specific methods, passing these to the {user_type} Menu so that 
                # they can be called by the user. If security has been 
                # activated, pass this on to the user object to ensure 
                # security methods are called within user methods.  
                if user_type == "admin":
                                                                                                  
                    # Set security setting for Security object,
                    # so that sanitise_input() method runs if security is 
                    # set to True.                   
                    self.secure_app.security = self.security
                    
                    user = Admin(self.login_email, self.password, 
                                 self.secure_app, security=self.security)

                    user_menu = AdminMenu("Profile", "Name search", 
                                          "Enrol new student", 
                                          "Unregister a student", 
                                          "Students", 
                                          user.view_user_profile, 
                                          user.search_for_user_by_name, 
                                          user.enrol_student, 
                                          user.delete_student, 
                                          user.view_students)
                    
                    user_menu.show_menu() # Move user on to their user menu.                                        
                    
                elif user_type == "teacher":
                                                            
                    self.secure_app.security = self.security 
                    
                    user = Teacher(self.login_email, self.password, 
                                   self.secure_app, security=self.security)

                    # Lesson object instantiated to give non-admin user access
                    # to lesson methods.
                    lesson = Lesson(user.subject, security=self.security)
                    
                    user_menu = TeacherMenu("Profile", "View my students",
                                            "My lessons", "Current lesson",
                                            "New lesson", "Update lesson",
                                            "Assign grade",
                                            user.view_user_profile,
                                            user.view_assigned_students, 
                                            lesson.view_all_my_lessons,
                                            lesson.view_my_active_lesson,
                                            lesson.add_new_lesson, 
                                            lesson.update_lesson,
                                            lesson.assign_grade)                                        
                    
                    user_menu.show_menu()   
                    
                elif user_type == "student":
                    
                    self.secure_app.security = self.security
                    
                    user = Student(self.login_email, self.password, 
                                   self.secure_app, security=self.security)                                        
                                        
                    lesson = Lesson(user.subject, security=self.security)

                    user_menu = StudentMenu("Profile", "View my teacher",
                                            "My lessons", "Current lesson",
                                            "Submit answers",
                                            user.view_user_profile,
                                            user.view_assigned_teacher,
                                            lesson.view_all_my_lessons,
                                            lesson.view_my_active_lesson,   
                                            lesson.add_answers)
                    
                    user_menu.show_menu()                            
            
        print(f"Your {user_type} email address or password is incorrect.")
            
        # If security has been activated, count login attempts, ready 
        # to pass to Security class.            
        if self.security:
            self.attempts += 1
        
        # If max login attempts made, reset attempts.
        if self.attempts == 5:
            self.attempts = 1            
        
        # If security has been activated, re-load login menu with security,
        # otherwise, keep it as default (deactivated).    
        if self.security:
            new_menu = LoginMenu(security=True, attempts=self.attempts)
        else:
            new_menu = LoginMenu()    

# Instantiate the login menu as first screen of the program.
new_menu = LoginMenu()
