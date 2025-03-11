import streamlit as st

# Navigation function
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()
st.set_page_config(page_title="Sports analytices using performance optimization", page_icon="🏏")
def home_page():
    #add info about the eye disease detection system in the sidebar
    st.markdown(
    """
    <style>
    /* Apply background image to the main content area */
    .main {
        background-image: url(https://img.freepik.com/free-vector/battle-screen-versus-vs-background-template-design_1017-27090.jpg?t=st=1741411503~exp=1741415103~hmac=a43e131f889d903f8da2953c817e812869f524da3bb117402e5648d70918e7a6&w=1800);  
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="text-align: center; padding: 1px; background-color: red ; border-radius: 5px; border: 2px solid black;">
            <p style="color: white; font-size: 33px; font-family: 'Times New Roman', cursive;">Sports Analytics Using Performance Optimization</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    #add image
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://t3.ftcdn.net/jpg/07/99/08/40/240_F_799084041_KEO7xcHSFIUbNy1BUSmbhkSL7c65Qg5N.jpg" alt="Liver" width="400" height=500">
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5,col6 = st.columns([1, 1, 1, 1, 1,1])
    with col2:
        if st.button("Login",type="primary"):
            navigate_to_page("login")
    with col5:
        if st.button("Sign Up",type="primary"):
            navigate_to_page("signup")
