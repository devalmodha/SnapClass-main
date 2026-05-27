import streamlit as st

from src.screen.home_screen import home_screen
from src.screen.teacher_screen import teacher_screen
from src.screen.student_screen import student_screen

# import streamlit as st
# st.write("URL:", st.secrets["SUPABASE_URL"])

# from src.database.config import supabase
# try:
#     r = supabase.table("teachers").select("*").limit(1).execute()
#     st.success("✅ Connected successfully!")
# except Exception as e:
#     st.error(f"❌ Error: {e}")

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