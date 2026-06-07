
import streamlit as st
from src.screen.home_screen import home_screen
from src.screen.teacher_screen import teacher_screen
from src.screen.student_screen import student_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendance Faster Using AI',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    # ✅ Get join code first
    join_code = st.query_params.get('join-code')
    
    # ✅ Redirect to student BEFORE rendering anything
    if join_code and st.session_state['login_type'] != 'student':
        st.session_state['login_type'] = 'student'
        st.rerun()

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
            if join_code and st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
                auto_enroll_dialog(join_code)
        case None:
            home_screen()

main()