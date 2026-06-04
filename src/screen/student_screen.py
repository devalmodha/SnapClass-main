import streamlit as st
from src.ui.base_layout import style_background_dashbord,style_base_layout
from src.components.header import header_deshbord
from src.components.footer import footer_deshbord
from PIL import Image 
import numpy as np
from src.pipline.face_pipline import predict_attendence, get_face_embeddings,trained_classifier
from src.pipline.voice_pipline import get_voice_embedding
from src.database.db import get_all_students,create_student,get_students_subjects,get_students_attendance,unenroll_student_to_subject
import time
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card



def student_dashbord():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        st.subheader(f"""welcome ,{student_data['name']}""") 
        if st.button("Logout",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()   


    st.space()

    c1 , c2 = st.columns(2)

    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject',type='primary',width='stretch'):
            enroll_dialog()    

    st.divider()    

    with st.spinner('Loading Your Enrolled Subjects....!'):
        subjects = get_students_subjects(student_id)
        logs = get_students_attendance(student_id)    

        stats_map = {}

        for log in logs:
            sid = log['subject_id']

            if sid not in stats_map:
                stats_map[sid] = {"total":0,"attended":0}

            stats_map[sid]['total'] +=1

            if logs.get('is_present'):
                stats_map[sid]['attended']+=1  

        cols = st.columns(2)
        for i,sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']

            stats = stats_map.get(sid,{"total":0,"attended":0})
            def unenroll_button():
                if st.button("unenroll from this course",type='tertiary',width='stretch',icon=':material/delete_forever:'):
                    unenroll_student_to_subject(student_id,sid)
                    st.toast(f"unenrollled from this {sub['name']} succesfully...!")
                    st.rerun()
                    

            with cols[i % 2]:
                subject_card(
                    name = sub['name'],
                    code = sub['subject_code'],
                    section = sub['section'],
                    stats = [
                        ('📆','Total',stats['total']),
                        ('✅','Attended',stats['attended']),
                    ],
                    footer_callback=unenroll_button
                )         
    footer_deshbord()

    

def student_screen():
    style_background_dashbord()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashbord()
        return

    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        if st.button("Go back to HOME",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()    
    
    

    st.space()
    st.space()
    st.header('Login using faceID ',text_alignment='center')

    show_registration = False

    photo_source = st.camera_input("position your face in the center")
    if photo_source:
        img = np.array(Image.open(photo_source))
        with st.spinner(' Ai is Scanning....!'):
            detected, all_ids,num_faces = predict_attendence(img)

            if num_faces ==0:
                st.warning('face not found')
            elif num_faces > 1:
                st.warning('multiple faces found')
            else :
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id']==student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f""" welcome {student['name']}""")

                        time.sleep(1)
                        st.rerun()

                else :
                    st.info('face not recorganize ! you might be a new student')
                    show_registration = True 

    if show_registration :
        with st.container(border=True):
            st.header("register  new profile")
            new_name = st.text_input("Enter Your Name:",placeholder="E.g riya sharma")

            st.subheader('Optional : Voice Enrollment')   
            st.info('Enroll for voice only Attendance ')

            audio_data = None
            try :
                audio_data =st.audio_input('record a short phrese like  I am present , My name is riya ')
            except Exception:
                st.error('Audio data failed!')    

            if st.button('Create Account',type='primary'):
                if new_name:
                    with st.spinner('creating profile...'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name,face_embedding = face_emb, voice_embedding=voice_emb)
                            if response_data :
                                trained_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f""" profile created ! hi {new_name}""")
                                time.sleep(1)
                                st.rerun()
                        else :
                            st.error('couldent capture your facial feature for registration')        



                else :
                    st.error('please enter your name!')            


    footer_deshbord()
