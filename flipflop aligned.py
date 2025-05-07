import streamlit as st
import hashlib

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
    seed = sum(ord(c) for c in username + transformed_password)
    state = seed % 256
    token_parts = []
    for _ in range(6):
        state = (state * 7 + 11) % 256
        token_parts.append(format(state, '02x'))
    return ''.join(token_parts)

# ---------- Session Initialization ----------
if 'user_db' not in st.session_state:
    st.session_state.user_db = {}

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
            token = generate_token(username, transformed)
            st.session_state.user_db[username] = {
                'transformed': transformed,
                'encrypted': encrypted,
                'token': token
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
            if encrypted == st.session_state.user_db[username]['encrypted']:
                st.success("✅ Login successful!")
                st.info(f"🔁 Transformed Password: `{transformed}`")
                st.info(f"🔒 Encrypted Password: `{encrypted}`")
                st.info(f"🔑 Token: `{st.session_state.user_db[username]['token']}`")
            else:
                st.error("❌ Incorrect password!")

# ---------- View Registered Users ----------
elif menu == "View Registered Users":
    st.subheader("📋 Registered Users")
    if not st.session_state.user_db:
        st.warning("No users registered yet.")
    else:
        for uname, data in st.session_state.user_db.items():
            st.markdown(f"""
            #### 👤 Username: `{uname}`
            - 🔁 Transformed: `{data['transformed']}`
            - 🔒 Encrypted: `{data['encrypted']}`
            - 🔑 Token: `{data['token']}`
            """)
