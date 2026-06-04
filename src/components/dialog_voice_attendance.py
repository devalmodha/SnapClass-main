import streamlit as st
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.pipline.voice_pipline import proces_bulk_audio
from src.components.dialog_attendance_result import show_attendance_result


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write('record audio of student saying i am present. then AI will recorgnize the student')

    audio_data = None

    audio_data = st.audio_input("Record Classroom audio")

    if st.button('Analyze Audio',width='stretch',type='primary'):
        with st.spinner('Processing Audio Data'):
            enrolled_res = supabase.table('subject_student').select("*,students(*)").eq('subject_id',selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.Warning('No Students enrolled in this course')
                return 
            candidates_dict = {
                s['students']['student_id'] : s['students']['voice_embedding']
                for s in enrolled_students if s['students'].get('voice_embedding')

            }
            if not candidates_dict:
                st.error('no enrolled students have voice profiles registred')
                return
            
            audio_bytes = audio_data.read()

            detected_scores = proces_bulk_audio(audio_bytes,candidates_dict)

            results,attendance_to_log = [],[]

            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'],0.0)
                is_present = bool(score > 0) 

                results.append({
                    "Name":student['name'],
                    "Id":student['student_id'],
                    "source": score if is_present else "_",
                    "status":" ✅present" if is_present else " ❌Absent"
                })

                attendance_to_log.append({
                    'student_id':student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp':current_timestamp,
                    'is_present':bool(is_present)
                })
            st.session_state.voice_attendance_results = (pd.DataFrame(results),attendance_to_log)   
    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results,logs =  st.session_state.voice_attendance_results
        show_attendance_result(df_results,logs)
               

                