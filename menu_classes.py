import requests

###### CHange print statments  to returns?

class Menu:
   
    def __init__(self, option_1, option_2, method_1, method_2):
        '''Allows for the creation of main menus and sub-menus'''
       
        self.option_1 = option_1
        self.option_2 = option_2
                       
        self.method_1 = method_1
        self.method_2 = method_2        
                
                   

class AdminMenu(Menu):
    
    def __init__(self, option_3, option_4, method_3, method_4):
        '''Allows for the creation of main menus and sub-menus'''
        super().__init__(self, self.option_1, self.option_2, self.method_1, self.method_2)
        self.option_3 = option_3
        self.option_4 = option_4
                       
        self.method_3 = method_3
        self.method_4 = method_4        
 
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
        :       ''').lower()             
 
          if menu == self.option_1[0].lower():
            self.method_1()               
 
          elif menu == self.option_2[0].lower():
            self.method_2()                                                                    
                
          else:
            print("\n!! Choose a valid option. !!\n")     
    

class LoginMenu():
    
    API_URL = "http://127.0.0.1:5000"
    
    ############## Add security instantiation if security on!

    def __init__(self):
        self.admin_list = requests.get(f"{self.API_URL}/admin_list", headers={"Content-Type": "application/json"}).json()        
        self.teacher_list = requests.get(f"{self.API_URL}/teacher_list", headers={"Content-Type": "application/json"}).json()
        self.student_list = requests.get(f"{self.API_URL}/student_list", headers={"Content-Type": "application/json"}).json()
        
        
        self.login_email = str(input("Enter your email address: "))
        self.password = str(input("Enter you password: "))

        self.show_menu()

    def show_menu(self):
        if "admin" in str(self.login_email):            
            user_type ="admin"
            user_list = self.admin_list            
            
            
        elif "teacher" in str(self.login_email):            
            user_type ="teacher"
            user_list = self.teacher_list
            
        elif "student" in str(self.login_email):
            user_type ="student"
            user_list = self.student_list
            
        else:
            print("That email address is not valid.")

        print(self.login_email, self.password)
        
        for user in user_list:
                
            if self.login_email == user["login_email"] and self.password == user["hashed_password"]:
                print("checking user type...")
                if user_type == "admin":
                    #user_menu = AdminMenu(ARGS?)
                    print(user_type)
                elif user_type == "teacher":
                    #user_menu = TeacherMenu(ARGS?)
                    print(user_type)
                elif user_type == "student":
                    #user_menu = StudentMenu(ARGS?)
                    print(user_type)                      
                else:
                    print(f"Your {user_type} email address or password is incorrect.")
    
   
new_menu = LoginMenu()
