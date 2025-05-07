import streamlit as st
import hashlib
import time

# In-memory database (reset on each run)
user_db = {}
login_attempts = {}
lockout_time = {}

MAX_ATTEMPTS = 3
LOCKOUT_TIME = 60  # seconds

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
    seed = sum(ord(c) for c in username + transformed_password)
    state = seed % 256
    token_parts = []
    for _ in range(6):
        state = (state * 7 + 11) % 256
        token_parts.append(format(state, '02x'))
    return ''.join(token_parts)

def register_user(username, password):
    if username in user_db:
        return "🚫 Username already exists!"
    transformed = flip_flop_transform(password)
    encrypted = encrypt_password(transformed)
    token = generate_token(username, transformed)
    user_db[username] = {
        'transformed': transformed,
        'encrypted': encrypted,
        'token': token
    }
    return "✅ Registration successful!"

def login_user(username, password):
    if username not in user_db:
        return "⚠️ User not found!"

    if username in lockout_time:
        time_diff = time.time() - lockout_time[username]
        if time_diff < LOCKOUT_TIME:
            wait = int(LOCKOUT_TIME - time_diff)
            return f"⏳ Locked out. Try again in {wait} seconds."
        else:
            del lockout_time[username]
            login_attempts[username] = 0

    transformed = flip_flop_transform(password)
    encrypted = encrypt_password(transformed)

    if encrypted == user_db[username]['encrypted']:
        login_attempts[username] = 0
        return (
            f"✅ Login successful!\n\n"
            f"🔁 Transformed: `{transformed}`\n"
            f"🔒 Encrypted: `{encrypted}`\n"
            f"🔑 Token: `{user_db[username]['token']}`"
        )
    else:
        login_attempts[username] = login_attempts.get(username, 0) + 1
        remaining = MAX_ATTEMPTS - login_attempts[username]
        if remaining <= 0:
            lockout_time[username] = time.time()
            return f"⛔ Too many attempts. Locked for {LOCKOUT_TIME} seconds."
        else:
            return f"❌ Incorrect password. Attempts left: {remaining}"

# UI Layout
st.set_page_config(page_title="Flip-Flop Auth System", layout="centered")

st.title("🔐 Flip-Flop Authentication System")

page = st.sidebar.selectbox("Navigate", ["Register", "Login", "View Users"])

if page == "Register":
    st.header("📝 Register")
    with st.form("register_form"):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        submitted = st.form_submit_button("Register")
        if submitted:
            if username and password:
                msg = register_user(username, password)
                st.success(msg) if msg.startswith("✅") else st.error(msg)
            else:
                st.warning("Please fill in all fields.")

elif page == "Login":
    st.header("🔑 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username and password:
                msg = login_user(username, password)
                if msg.startswith("✅"):
                    st.success(msg)
                elif msg.startswith("🔁") or msg.startswith("🔒"):
                    st.info(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Please fill in all fields.")

elif page == "View Users":
    st.header("📋 Registered Users")
    if not user_db:
        st.info("No users registered yet.")
    else:
        for user, data in user_db.items():
            st.markdown(f"""
                **👤 Username:** `{user}`  
                **🔁 Transformed:** `{data['transformed']}`  
                **🔒 Encrypted:** `{data['encrypted']}`  
                **🔑 Token:** `{data['token']}`
                ---
            """)
