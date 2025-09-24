import streamlit as st
import requests
import re
import base64

# --- CONFIGURATION ---
st.set_page_config(
    page_title="PawFinder",
    page_icon="🐾",
    layout="wide"
)
DJANGO_API_URL = "http://127.0.0.1:8000/api/"

# --- HELPER FUNCTIONS ---

def get_image_as_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- MODIFIED BANNER FUNCTION ---
def show_banner(height, img_v_pos, text_v_pos, text_h_pos):
    """
    Displays the banner using parameters from the editor.
    """
    img_base64 = get_image_as_base64("banner.jpg")
    
    st.markdown(
        f"""
        <style>
        .banner-container {{
            position: relative;
            text-align: center;
            color: black;
            height: {height}px; /* Controlled by slider */
            overflow: hidden;

            /* --- CSS for Full-Width Banner --- */
            width: 100vw;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
        }}
        .banner-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center {img_v_pos}%; /* Controlled by slider */
        }}
        .banner-title {{
            position: absolute;
            top: {text_v_pos}%; /* Controlled by slider */
            left: {text_h_pos}%; /* Controlled by slider */
            transform: translate(-50%, -50%);
            font-size: 4rem;
            font-weight: bold;
            text-shadow: 2px 2px 8px #ffffff;
        }}
        </style>
        <div class="banner-container">
            <img class="banner-image" src="data:image/jpeg;base64,{img_base64}">
            <h1 class="banner-title">🐾 PawFinder</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

def validate_password(password):
    errors = []
    if len(password) < 8: errors.append("At least 8 characters")
    if not re.search(r"[A-Z]", password): errors.append("At least one uppercase letter")
    if not re.search(r"[a-z]", password): errors.append("At least one lowercase letter")
    if not re.search(r"[0-9]", password): errors.append("At least one number")
    if not re.search(r"[!@#$%^&*(),.?:{}|<>]", password): errors.append("At least one special character")
    return errors

def switch_page(page_name):
    st.session_state.page = page_name

# --- MAIN APP ---

# --- INTERACTIVE EDITOR ---
with st.expander("🎨 Banner Editor (Use this to find the perfect values)"):
    st.subheader("Banner Size")
    height_val = st.slider("Banner Height (px)", 100, 800, 300)

    st.subheader("Image Position")
    img_pos_val = st.slider("Image Vertical Focus (%)", 0, 100, 70, help="0% is top, 100% is bottom.")

    st.subheader("Text Position")
    text_pos_v_val = st.slider("Text Vertical Position (%)", 0, 100, 40)
    text_pos_h_val = st.slider("Text Horizontal Position (%)", 0, 100, 50)

# --- PAGE DISPLAY ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Pass the editor values to the banner function
show_banner(height_val, img_pos_val, text_pos_v_val, text_pos_h_val)

# --- PAGE 1: HOME (LOGIN) ---
if st.session_state.page == 'Home':
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 1.5, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("Member Login")
                username = st.text_input("Username", label_visibility="collapsed", placeholder="Username")
                password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
                st.form_submit_button("Login")

            st.write("New user?")
            st.button("Register", on_click=switch_page, args=('Register',), use_container_width=True)


# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'Register':
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.title("Create a PawFinder Account")
            with st.form("registration_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=1, max_value=120, step=1)
                city = st.text_input("City")
                phone_number = st.text_input("Phone Number")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                validation_messages = validate_password(" ")
                st.caption("Password must contain: " + ", ".join(validation_messages))

                if st.form_submit_button("Register"):
                    password_errors = validate_password(password)
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    elif password_errors:
                        st.error("Password is not strong enough. Please check the rules.")
                    else:
                        registration_data = {
                            "username": username, "email": email, "name": name,
                            "password": password, "age": age, "city": city,
                            "phone_number": phone_number
                        }
                        try:
                            response = requests.post(f"{DJANGO_API_URL}register/", json=registration_data)
                            if response.status_code == 201:
                                st.success("Registration successful! Welcome to the community! 🐾")
                            else:
                                st.error(f"Registration failed: {response.json().get('error', 'Unknown error')}")
                        except requests.exceptions.ConnectionError:
                            st.error("Could not connect to the server.")

            st.button("Back to Login", on_click=switch_page, args=('Home',), use_container_width=True)
