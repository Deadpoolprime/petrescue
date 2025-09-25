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

# It's good practice to fetch this from st.secrets in a deployed app
DJANGO_API_URL = "http://127.0.0.1:8000/api/"

# --- HELPER FUNCTIONS ---

def get_image_as_base64(path):
    """Encodes a local image file to a base64 string."""
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Banner image not found at path: {path}. Please make sure 'banner.jpg' is in the root directory.")
        return None

def validate_password(password):
    """Checks a password against a set of rules."""
    # Corrected to check the actual password, not a space
    if not password or password.isspace():
        return ["Password cannot be empty."]
    errors = []
    if len(password) < 8: errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", password): errors.append("at least one uppercase letter")
    if not re.search(r"[a-z]", password): errors.append("at least one lowercase letter")
    if not re.search(r"[0-9]", password): errors.append("at least one number")
    if not re.search(r"[!@#$%^&*(),.?:{}|<>]", password): errors.append("at least one special character")
    return errors

def switch_page(page_name):
    """Switches the 'page' value in st.session_state."""
    st.session_state.page = page_name

# --- BANNER (Hardcoded Values) ---
# The interactive editor has been removed.
# We now define the banner's style directly with fixed values.
img_base64 = get_image_as_base64("banner.jpg")
if img_base64:
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 1rem;
        }}
        .banner-container {{
            position: relative;
            text-align: center;
            color: black;
            height: 300px; /* <<< HARDCODED VALUE (was height_val) */
            overflow: hidden;
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
            object-position: center 70%; /* <<< HARDCODED VALUE (was img_v_pos) */
        }}
        .banner-title {{
            position: absolute;
            top: 40%; /* <<< HARDCODED VALUE (was text_v_pos) */
            left: 50%; /* <<< HARDCODED VALUE (was text_h_pos) */
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

# --- PAGE ROUTING LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'


# --- PAGE 1: HOME (LOGIN) ---
if st.session_state.page == 'Home':
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Member Login")
            username = st.text_input("Username", label_visibility="collapsed", placeholder="Username")
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
            
            # TODO: Add login logic here
            submitted = st.form_submit_button("Login")
            if submitted:
                st.info("Login functionality is not yet implemented.")

        st.write("---")
        st.write("New user?")
        st.button("Register", on_click=switch_page, args=('Register',), use_container_width=True)


# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'Register':
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.title("Create a PawFinder Account")
        with st.form("registration_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=120, step=1, help="You must be 18 or older to register.")
            city = st.text_input("City")
            phone_number = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            st.caption("Password must contain: at least 8 characters, one uppercase, one lowercase, one number, and one special character.")

            if st.form_submit_button("Register"):
                password_errors = validate_password(password)
                if password != confirm_password:
                    st.error("Passwords do not match.")
                elif password_errors:
                    st.error(f"Password is not strong enough. It's missing: {', '.join(password_errors)}.")
                else:
                    registration_data = {
                        "username": username, "email": email, "name": name,
                        "password": password, "age": age, "city": city,
                        "phone_number": phone_number
                    }
                    try:
                        response = requests.post(f"{DJANGO_API_URL}register/", json=registration_data)
                        response.raise_for_status() # Raises an error for bad status codes

                        st.success("Registration successful! Welcome! 🐾 You will be redirected to the login page.")
                        st.balloons()
                        
                        # Set the page to 'Home'. The script will rerun automatically after the form submission
                        # and display the Home page.
                        switch_page('Home')
                        
                        # --- REMOVED st.experimental_rerun() ---

                    except requests.exceptions.HTTPError as e:
                        try:
                            error_detail = e.response.json()
                            st.error(f"Registration failed: {error_detail.get('detail', 'Please check your inputs.')}")
                        except ValueError:
                            st.error(f"Registration failed with status code {e.response.status_code}. Server sent an invalid response.")
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the server. Is it running?")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

        st.write("---")
        st.button("Back to Login", on_click=switch_page, args=('Home',), use_container_width=True)