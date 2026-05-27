import streamlit as st
from src.ui.base_layout import style_background_dashbord,style_base_layout
from src.components.header import header_deshbord
from src.components.footer import footer_deshbord
from PIL import Image 
import numpy as np

def student_screen():
    style_background_dashbord()
    style_base_layout()

    c1,c2 = st.columns(2,vertical_alignment='center',gap='xxlarge')
    with c1 :
        header_deshbord()
    with c2 :
        if st.button("Go back to HOME",type='secondary',key='loginbackbtn',shortcut="control+backspace"):
            st.session_state['login-type'] = None
            st.rerun()    
    
    

    st.space()
    st.space()
    st.header('Login using faceID ',text_alignment='center')
    photo_source = st.camera_input("position your face in the center")
    if photo_source:
        np.array(Image.open(photo_source))

    footer_deshbord()
