import streamlit as st
from src.ui.base_layout import style_background_dashbord,style_base_layout
from src.components.header import header_deshbord
from src.components.footer import footer_deshbord
from src.database.db import check_teacher_exists,create_teacher,teacher_login,get_teacher_subjects,get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipline.face_pipline import predict_attendence
import numpy as np
import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_result import attendence_result_dialog
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


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
    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        st.subheader(f"""welcome ,{teacher_data['name']}""") 
        if st.button("Logout",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()   


    st.space()
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1,tab2,tab3 = st.columns(3)

    with tab1:
       type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
       if st.button("Take Attendance",type=type1,width='stretch',icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"

        if st.button("Manage Subjects",type=type2,width='stretch',icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()    
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_record" else "tertiary"

        if st.button("Attendance Record",type=type3,width='stretch',icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = "attendance_record"
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_record":
        teacher_tab_attendance_record()        
            



    footer_deshbord()        
       
def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    
    st.header('Take AI Attendance')

    if 'attendance_image' not in st.session_state:
        st.session_state.attendance_image = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning('You Havent Created any subjects yet! please create one to begin !')
        return
    
    subject_option = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1 , col2 = st.columns([3,1],vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject' ,options=list(subject_option.keys()))


    with col2 :
        if st.button('Add Photos',type='primary',width='stretch',icon=':material/photo_prints:'):
            add_photos_dialog()    

    selected_subject_id = subject_option[selected_subject_label]

    st.divider()  

    if st.session_state.attendance_image:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx,img in enumerate(st.session_state.attendance_image):
            with gallery_cols[idx %4]:
                st.image(img,width='stretch',caption=f'photo{idx+1}')
    has_photos = bool(st.session_state.attendance_image)

    c1,c2,c3 = st.columns(3) 

    with c1:
        if st.button('Clear All Photos',width='stretch',type='tertiary',icon=':material/delete:',disabled= not has_photos):
            st.session_state.attendance_image = []
            st.rerun()             

    with c2:
        
        if st.button('Run Face Analysis', width='stretch',type='secondary',icon=':material/analytics:',disabled= not has_photos):
            with st.spinner('Deep Scanning Classroom Photoes....'):
                all_detected_id = {}

                for idx,img in enumerate(st.session_state.attendance_image):
                    img_np = np.array(img.convert('RGB'))
                    detected ,_,_ = predict_attendence(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_id.setdefault(student_id,[]).append(f"Photo {idx+1}")
                enrolled_res = supabase.table('subject_student').select("*,students(*)").eq('subject_id',selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.Warning('No Students enrolled in this course')
                else:
                    results,attendance_to_log = [],[]

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_id.get(int(student['student_id']),[])
                        is_present = len(sources) > 0

                        results.append({
                            "Name":student['name'],
                            "Id":student['student_id'],
                            "source": ",".join(sources) if is_present else "_",
                            "status":" ✅present" if is_present else " ❌Absent"
                        })

                        attendance_to_log.append({
                            'student_id':student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp':current_timestamp,
                            'is_present':bool(is_present)
                        })
                attendence_result_dialog(pd.DataFrame(results),attendance_to_log)
    with c3:
        if st.button('Voice Attendance',width='stretch',type='primary',icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)




def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage subjects')
    with col2:
        if st.button("Create New Subject", width='stretch'):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students", sub['total_students']),  
                ("🕰️", "Classes", sub['total_classes'])
            ]

            def share_btn():  
                if st.button(f"Share Code: {sub['name']}", key=f"Share_{sub['subject_code']}", icon=":material/share:"):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.write("")

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
    else:
        st.info("No subjects found. Create one above!")
def  teacher_tab_attendance_record():
    st.header("Attendance Record") 

    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return

    data = []

    for r in records:
        ts = r.get('timestamp')

    data.append({
        "ts_group": ts.split(":")[0] if ts else None,
        "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
        "Subject": r['subjects']['name'],
        "Subject Code": r['subjects']['subject_code'],
        "is_present": bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)


    summary = (
    df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
      .agg(
          Present_Count=('is_present', 'sum'),
          Total_Count=('is_present', 'count')
      )
      .reset_index()
    )

    summary['Attendance Stats'] = (
    "✅ " + summary['Present_Count'].astype(str) + "/" 
    + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = (
    summary.sort_values(by='ts_group', ascending=False)
           [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
        )
    
    st.dataframe(display_df,width='stretch',hide_index=True)



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
            st.session_state['login_type'] = None
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
            st.session_state['login_type'] = None
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

       