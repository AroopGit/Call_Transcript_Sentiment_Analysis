import streamlit as st
import bcrypt
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
import altair as alt

# Database Functions
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

def add_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
    conn.commit()

def authenticate_user(username, password):
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if result:
        stored_password = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    return False

def login():
    st.title("📞 Call Transcript Sentiment Analysis Tool - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.success("Login successful! ✅")
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password.")

def register():
    st.title("📞 Call Transcript Sentiment Analysis Tool - Register")
    username = st.text_input("Create a Username")
    password = st.text_input("Create a Password", type="password")

    if st.button("Register"):
        if username and password:
            add_user(username, password)
            st.success("User registered successfully! ✅ Please log in.")
        else:
            st.error("Please enter a valid username and password.")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    auth_option = st.sidebar.selectbox("Choose an option", ["Login", "Register"])

    if auth_option == "Login":
        login()
    else:
        register()
else:
    st.sidebar.write(f"Welcome, {st.session_state['username']}!")

    sentiment_analysis = pipeline("sentiment-analysis")

    uploaded_file = st.file_uploader("📄 Upload Call Transcript (Text File)", type=["txt"])

    if uploaded_file:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with open(uploaded_file.name, "r") as file:
            transcripts = file.readlines()

        results = []
        positive_scores = []
        negative_scores = []

        for transcript in transcripts:
            sentiment = sentiment_analysis(transcript)[0]
            label = sentiment["label"]
            score = sentiment["score"]

            if label == "POSITIVE":
                positive_scores.append(score)
            else:
                negative_scores.append(1 - score)

            results.append({"Transcript": transcript.strip(), "Sentiment": label, "Score": score})

        total_lines = len(transcripts)
        avg_positive_score = sum(positive_scores) / total_lines if positive_scores else 0
        avg_negative_score = sum(negative_scores) / total_lines if negative_scores else 0

        final_score = avg_positive_score - avg_negative_score
        final_score = max(0, min(final_score, 1))

        df = pd.DataFrame(results)
        st.write("### Sentiment Analysis Results", df)

        st.write("### Sentiment Distribution")
        sentiment_counts = df["Sentiment"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=140)
        st.pyplot(fig)

        st.write("### Positive vs Negative Lines (Bar Chart)")
        bar_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Sentiment", title="Sentiment"),
            y=alt.Y("count()", title="Count"),
            color="Sentiment"
        )
        st.altair_chart(bar_chart, use_container_width=True)

        st.write("### Sentiment Scores Over Time (Line Chart)")
        df['Line Number'] = range(1, len(df) + 1)
        line_chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("Line Number", title="Line Number"),
            y=alt.Y("Score", title="Sentiment Score"),
            color="Sentiment"
        )
        st.altair_chart(line_chart, use_container_width=True)

        st.write(f"### Final Sentiment Score: {final_score:.2f}")

        st.write("### 🛠️ Sales Tips Based on Sentiment")
        if final_score > 0.7:
            st.success("The overall sentiment is highly positive! Focus on closing the deal by offering a personalized discount or loyalty program.")
        elif 0.4 <= final_score <= 0.7:
            st.info("The sentiment is mostly neutral. Highlight the key benefits of your product and address any remaining concerns.")
        else:
            st.warning("The sentiment is leaning negative. Focus on empathizing with the customer's concerns and offering solutions to their problems.")
