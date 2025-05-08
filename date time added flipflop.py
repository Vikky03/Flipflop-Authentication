import streamlit as st
import hashlib
import time
from datetime import datetime
import pytz
import random

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

# Initialize persistent session state dictionaries
if 'user_db' not in st.session_state:
    st.session_state.user_db = {}

if 'login_history' not in st.session_state:
    st.session_state.login_history = {}

# Flip-Flop transformation
def flip_flop_transform(password):
    state = 0b1010
    transformed = []
    for ch in password:
        bit = ord(ch)
        state = state ^ bit
        transformed.append(chr((state + bit) % 128))
    return ''.join(transformed)

# SHA-256 encryption
def encrypt_password(transformed_password):
    return hashlib.sha256(transformed_password.encode()).hexdigest()

# Generate token
def generate_token(username, transformed_password):
    seed = sum(ord(c) for c in username + transformed_password + str(time.time()) + str(random.randint(1000, 9999)))
    state = seed % 256
    token_parts = []
    for _ in range(6):
        state = (state * 7 + 11) % 256
        token_parts.append(format(state, '02x'))
    return ''.join(token_parts)

# Set up navigation
st.set_page_config(page_title="Flip-Flop Auth", layout="centered")
st.sidebar.title("🔐 Flip-Flop Auth System")
page = st.sidebar.radio("Go to", ["Register", "Login", "View Registered Users"])

# Page 1: Register
if page == "Register":
    st.title("📝 User Registration")
    username = st.text_input("Enter a new username")
    password = st.text_input("Enter a new password", type="password")

    if st.button("Register"):
        if username in st.session_state.user_db:
            st.error("❌ Username already exists!")
        else:
            transformed = flip_flop_transform(password)
            encrypted = encrypt_password(transformed)
            st.session_state.user_db[username] = {
                'transformed': transformed,
                'encrypted': encrypted,
                'last_token': ""
            }
            st.session_state.login_history[username] = {
                'count': 0,
                'timestamps': [],
                'tokens': []
            }
            st.success("✅ User registered successfully!")

# Page 2: Login
elif page == "Login":
    st.title("🔑 User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username not in st.session_state.user_db:
            st.error("❌ User not found!")
        else:
            transformed = flip_flop_transform(password)
            encrypted = encrypt_password(transformed)

            if encrypted == st.session_state.user_db[username]['encrypted']:
                token = generate_token(username, transformed)
                login_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

                # Record login
                st.session_state.user_db[username]['last_token'] = token
                st.session_state.login_history[username]['count'] += 1
                st.session_state.login_history[username]['timestamps'].append(login_time)
                st.session_state.login_history[username]['tokens'].append(token)

                st.success("✅ Login successful!")
                st.code(f"Username: {username}")
                st.code(f"Transformed: {transformed}")
                st.code(f"Encrypted: {encrypted}")
                st.code(f"Login Time (IST): {login_time}")
                st.code(f"Token: {token}")
            else:
                st.error("❌ Incorrect password!")

# Page 3: View All Users
elif page == "View Registered Users":
    st.title("📋 All Registered Users")
    if not st.session_state.user_db:
        st.info("ℹ️ No users registered yet.")
    else:
        for username, data in st.session_state.user_db.items():
            st.subheader(f"👤 Username: {username}")
            st.text(f"🔁 Transformed: {data['transformed']}")
            st.text(f"🔒 Encrypted: {data['encrypted']}")
            st.text(f"🔑 Last Token: {data['last_token']}")
            st.text(f"🕓 Total Logins: {st.session_state.login_history[username]['count']}")

            with st.expander("📜 Login History"):
                for i, timestamp in enumerate(st.session_state.login_history[username]['timestamps']):
                    token = st.session_state.login_history[username]['tokens'][i]
                    st.write(f"{i+1}. {timestamp} → Token: {token}")
