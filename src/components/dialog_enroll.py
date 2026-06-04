import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog("Enroll In Subject ")
def enroll_dialog():
    st.write("Enter The Subject Code Provided By Your Teacher To Enroll")
    join_code = st.text_input('subject Code',placeholder = 'eg. CS101')
    if st.button('Enroll Now',type='primary',width='stretch'):

        if join_code:
            res = supabase.table('subjects').select('subject_id,name,subject_code').eq('subject_code',join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_student').select('*').eq('subject_id',subject['subject_id']).eq('student_id',student_id).execute()

                if check.data:
                    st.warning('you are already enrolled in this program')
                else:
                    enroll_student_to_subject(student_id,subject['subject_id'])  
                    st.success('successfully enrolled !!')
                    time.sleep(2)
                    st.rerun()  
        else:
            st.warning('Please Enter a Subject Code')        