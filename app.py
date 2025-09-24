import streamlit as st
import requests
import re

# --- CONFIGURATION ---
DJANGO_API_URL = "http://127.0.0.1:8000/api/"

# --- HELPER FUNCTIONS ---
def validate_password(password):
    """Returns a list of error messages if password is not strong enough."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?:{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    return errors

def switch_page(page_name):
    """Function to switch the page in session state."""
    st.session_state.page = page_name

# --- MAIN APP ---

# Initialize session state for page navigation if it doesn't exist
if 'page' not in st.session_state:
    st.session_state.page = 'Login'

# --- PAGE 1: LOGIN ---
if st.session_state.page == 'Login':
    st.title("Pet Rescue Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.form_submit_button("Login")
        
        if login_button:
            # Note: Login API endpoint is not created yet. This is a placeholder.
            st.warning("Login functionality is not yet implemented in the backend.")

    st.write("---")
    st.write("Don't have an account?")
    st.button("Register Here", on_click=switch_page, args=('Register',))

# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'Register':
    st.title("Create a New Account")

    with st.form("registration_form"):
        st.write("Please fill in the details below to register.")
        
        # **FIX**: Add separate fields for username and email
        username = st.text_input("Username")
        email = st.text_input("Email")
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        city = st.text_input("City")
        phone_number = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        st.caption("""
        Password must contain:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """)
        confirm_password = st.text_input("Confirm Password", type="password")

        submit_button = st.form_submit_button("Register")

        if submit_button:
            password_errors = validate_password(password)
            if password != confirm_password:
                st.error("Passwords do not match.")
            elif password_errors:
                for error in password_errors:
                    st.error(error)
            else:
                # **FIX**: Prepare data with separate username
                registration_data = {
                    "username": username,
                    "email": email,
                    "name": name,
                    "password": password,
                    "age": age,
                    "city": city,
                    "phone_number": phone_number
                }
                
                try:
                    # Send data to Django API
                    response = requests.post(f"{DJANGO_API_URL}register/", json=registration_data)
                    
                    if response.status_code == 201:
                        st.success("Registration successful! You can now log in.")
                        st.balloons()
                    else:
                        # Show error message from the API
                        st.error(f"Registration failed: {response.json().get('error', 'Unknown error')}")

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the server. Please ensure the Django backend is running.")

    st.write("---")
    st.write("Already have an account?")
    st.button("Login Here", on_click=switch_page, args=('Login',))