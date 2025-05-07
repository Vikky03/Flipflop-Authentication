import streamlit as st
import hashlib
from datetime import datetime
import random

# ---------- Flip-Flop Authentication Functions ----------
def flip_flop_transform(password):
    state = 0b1010
    transformed = []
    for ch in password:
        bit = ord(ch)
        state = state ^ bit
        transformed.append(chr((state + bit) % 128))
    return ''.join(transformed)

def encrypt_password(transformed_password):
    return hashlib.sha256(transformed_password.encode()).hexdigest()

def generate_token(username, transformed_password):
    # Add timestamp & random seed for new token each time
    seed = sum(ord(c) for c in username + transformed_password) + int(datetime.now().timestamp()) + random.randint(1, 999)
    state = seed % 256
    token_parts = []
    for _ in range(6):
        state = (state * 7 + 11) % 256
        token_parts.append(format(state, '02x'))
    return ''.join(token_parts)

# ---------- Session Initialization ----------
if 'user_db' not in st.session_state:
    st.session_state.user_db = {}

if 'login_history' not in st.session_state:
    st.session_state.login_history = {}

# ---------- Page Selection ----------
st.set_page_config(page_title="Flip-Flop Auth System")
st.title("🔐 Flip-Flop Authentication System")

menu = st.sidebar.radio("Select Option", ["Register", "Login", "View Registered Users"])

# ---------- Register ----------
if menu == "Register":
    st.subheader("📝 Register New User")
    username = st.text_input("Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pass")
    if st.button("Register"):
        if username in st.session_state.user_db:
            st.error("❌ Username already exists!")
        else:
            transformed = flip_flop_transform(password)
            encrypted = encrypt_password(transformed)
            st.session_state.user_db[username] = {
                'transformed': transformed,
                'encrypted': encrypted,
                'last_token': "",
            }
            st.session_state.login_history[username] = {
                'count': 0,
                'timestamps': [],
                'tokens': []
            }
            st.success("✅ User registered successfully!")

# ---------- Login ----------
elif menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if username not in st.session_state.user_db:
            st.error("❌ User not found!")
        else:
            transformed = flip_flop_transform(password)
            encrypted = encrypt_password(transformed)
            stored_encrypted = st.session_state.user_db[username]['encrypted']
            if encrypted == stored_encrypted:
                # Successful login
                new_token = generate_token(username, transformed)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Update latest token
                st.session_state.user_db[username]['last_token'] = new_token

                # Update login history
                st.session_state.login_history[username]['count'] += 1
                st.session_state.login_history[username]['timestamps'].append(now)
                st.session_state.login_history[username]['tokens'].append(new_token)

                st.success("✅ Login successful!")
                st.info(f"🔁 Transformed Password: `{transformed}`")
                st.info(f"🔒 Encrypted Password: `{encrypted}`")
                st.info(f"🔑 New Token: `{new_token}`")
                st.info(f"🕒 Login Time: `{now}`")
            else:
                st.error("❌ Incorrect password!")

# ---------- View Registered Users ----------
elif menu == "View Registered Users":
    st.subheader("📋 Registered Users Info")
    if not st.session_state.user_db:
        st.warning("No users registered yet.")
    else:
        for uname, data in st.session_state.user_db.items():
            history = st.session_state.login_history.get(uname, {'count': 0, 'timestamps': [], 'tokens': []})
            st.markdown(f"""
            ---
            #### 👤 Username: `{uname}`
            - 🔁 Transformed Password: `{data['transformed']}`
            - 🔒 Encrypted Password: `{data['encrypted']}`
            - 🔑 Last Login Token: `{data['last_token']}`  
            - 🔢 Login Count: `{history['count']}`
            """)
            if history['timestamps']:
                with st.expander("📜 Login History"):
                    for i, (ts, token) in enumerate(zip(history['timestamps'], history['tokens']), 1):
                        st.markdown(f"{i}. 🕒 `{ts}` — 🔑 Token: `{token}`")
