import streamlit as st
from supabase import create_client,Client
import httpx


supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)
supabase.postgrest.session = httpx.Client(timeout=60.0)