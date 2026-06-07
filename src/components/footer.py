import streamlit as st 

def footer_home():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
                <div style = "margin-top:2rem; display:flex; gap : 6px;justify-content :center; item-align : center ">
                <p style="color : white; font-weight : bold">Created by Deval Modha</p>
                </div>    
            """,unsafe_allow_html=True)



def footer_deshbord():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
                <div style = "margin-top:2rem; display:flex; gap : 6px;justify-content :center; item-align : center ">
                <p style="color : black; font-weight : bold">Created by Deval Modha</p>
                </div>    
            """,unsafe_allow_html=True)