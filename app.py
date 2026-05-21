import streamlit as st

from src.screen.home_screen import home_screen
from src.screen.teacher_screen import teacher_screen
from src.screen.student_screen import student_screen

def main():
    if 'login-type' not in st.session_state:
        st.session_state['login-type'] = None

    match st.session_state['login-type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
           home_screen()
            



main()    