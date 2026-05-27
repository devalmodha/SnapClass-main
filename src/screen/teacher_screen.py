import streamlit as st
from src.ui.base_layout import style_background_dashbord,style_base_layout
from src.components.header import header_deshbord
from src.components.footer import footer_deshbord
from src.database.db import check_teacher_exists,create_teacher,teacher_login


def teacher_screen():
    style_background_dashbord()
    style_base_layout()
    
    if "teacher_data" in st.session_state:
        teacher_dashbord()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif  st.session_state.teacher_login_type=="register":   
        teacher_screen_register()

def teacher_dashbord():
    teacher_data = st.session_state.teacher_data
    st.header(f"""welcome ,{teacher_data['name']}""")    
    

def login_teacher(username,password):
    if not username or not password:  
        return False
    teacher = teacher_login(username,password)
    if teacher:
        st.session_state.user_role='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False  

def register_teacher(teacher_username,teacher_password,teacher_name,teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_password:
        return False,"All Fields are required !"
    
    if check_teacher_exists(teacher_username):
        return False,"username already taken"
    
    if teacher_password != teacher_pass_confirm:
        return False,"password doesnt match"
    try:
        create_teacher(teacher_username,teacher_password,teacher_name)
        return True,"Successfully created ! Login now"
    except Exception as e:
        return False,"unexpected error"    
        


def teacher_screen_login():
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        if st.button("Go back to HOME",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['login-type'] = None
            st.rerun()    
    st.header('Login using password ',text_alignment='center')

    st.space()
    st.space()

    teacher_username = st.text_input("Enter Username",placeholder='Enter Your Username')
    teacher_password = st.text_input("Enter Password",type='password',placeholder='Enter Your Password')
    st.divider()

    btnc1 ,btnc2 = st.columns(2)

    with btnc1:
        if st.button("LogIn",icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            if login_teacher(teacher_username,teacher_password):
                st.toast("Welcome back !!")
                import time 
                time.sleep(1)
                st.rerun()
            else:
                st.error("invalid username and password")    
    with btnc2:
        if st.button("Register Instead",type='primary',icon=':material/passkey:',width='stretch'):
            st.session_state.teacher_login_type ='register'    


    footer_deshbord()
    

def teacher_screen_register():  
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        if st.button("Go back to HOME",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['login-type'] = None
            st.rerun()    
    st.header('Register your  teacher profile')
    
    st.space()
    st.space()

    teacher_username = st.text_input("Enter Username",placeholder='Enter Your Username')

    teacher_name = st.text_input("Enter Name",placeholder='Enter Your Username')

    teacher_password = st.text_input("Enter Password",type='password',placeholder='Enter Your Password')

    teacher_pass_confirm = st.text_input("Confirm Password",type='password',placeholder='Enter Your Password')
    st.divider()

    btnc1 ,btnc2 = st.columns(2)

    with btnc1:
        if st.button("Register Now",icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            success,message = register_teacher(teacher_username,teacher_password,teacher_name,teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)    
    with btnc2:
        if st.button("LogIn Instead",type='primary',icon=':material/passkey:',width='stretch') :
            st.session_state.teacher_login_type ='login'    



    footer_deshbord()

       