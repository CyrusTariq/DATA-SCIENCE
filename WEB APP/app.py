import streamlit as st
import requests
import producer 
backend_url = "http://localhost:8000"

st.title("Data Science and Machine Learning Hub")

menu = ["Home", "Login", "Signup", "Articles", "Upload Article"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Home")
    st.write("Welcome to the Article Management System")

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{backend_url}/login/", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Logged in successfully")
            st.session_state["logged_in"] = True
        else:
            st.error("Login failed")

elif choice == "Signup":
    st.subheader("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    password_confirm = st.text_input("Confirm Password", type="password")
    if st.button("Signup"):
        if password == password_confirm:
            response = requests.post(f"{backend_url}/users/", json={"username": username, "password": password})
            print(response)
            if response.status_code in (201, 200):
                st.success("Account created successfully")
                #producer.send_msg(username)
            else:
                st.error("Signup failed")
                # producer.send_one(username)
                # producer.send_msg(username)
        else:
            st.warning("Passwords do not match")

elif choice == "Articles":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("Articles")
        response = requests.get(f"{backend_url}/articles/")
        if response.status_code == 200:
            articles = response.json()
            for article in articles:
                st.write(f"**{article['title']}**")
                st.write(article['content'])
                st.download_button(
                    label="Download PDF",
                    data=article['pdf'].encode('latin1'),
                    file_name=f"{article['title']}.pdf",
                    mime="application/pdf"
                )
                st.write("---")
        else:
            st.error("Failed to fetch articles")
    else:
        st.warning("Please log in to view the articles")

elif choice == "Upload Article":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader("Upload New Article")
        title = st.text_input("Title")
        content = st.text_area("Content")
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

        if st.button("Upload"):
            if title and content and pdf_file:
                files = {"pdf": pdf_file.getvalue()}
                response = requests.post(f"{backend_url}/articles/upload/", files={"pdf": pdf_file}, data={"title": title, "content": content})
                
                if response.status_code == 200:
                    st.success("Article uploaded successfully")
                else:
                    st.error("Failed to upload article")
            else:
                st.warning("Please fill out all fields")
        else:
            st.warning("Please log in to upload articles")

# elif choice == "PyCaret Integration":
#     st.subheader("PyCaret Integration")
#     pycaret_app_url = "http://pycaret:8502"
#     st.markdown(f"Visit the PyCaret app [here]({pycaret_app_url})")

