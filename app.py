# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import re
import base64

# --- Streamlit frontend ---

# Ensure queries.csv exists with the correct columns
CSV_FILE = "queries.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["student_id", "Query", "Timestamp", "response"]).to_csv(CSV_FILE, index=False)

# Ensure projects.csv exists for project submissions
PROJECTS_FILE = "projects.csv"
if not os.path.exists(PROJECTS_FILE):
    pd.DataFrame(columns=["student_id", "project_title", "Timestamp"]).to_csv(PROJECTS_FILE, index=False)

# Set page configuration with Ky’ra favicon/icon
# Use a bold, beautiful SVG icon for Ky’ra (embedded as base64)
KYRA_SVG = """
<svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="60" cy="60" r="54" fill="#4fb8ac" stroke="#222" stroke-width="6"/>
<text x="50%" y="58%" text-anchor="middle" fill="#fff" font-size="64" font-family="Segoe UI, Arial, sans-serif" font-weight="bold" dy=".3em">K</text>
</svg>
"""
def svg_to_base64(svg):
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

kyra_svg_base64 = svg_to_base64(KYRA_SVG)
kyra_icon_dataurl = f"data:image/svg+xml;base64,{kyra_svg_base64}"

st.set_page_config(
    page_title="Ask Ky’ra",
    page_icon=kyra_icon_dataurl,
    layout="centered"
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Roboto', sans-serif;
    }
    .stTextInput > div > input {
        border: 1px solid #ccc;
        border-radius: 5px;
        font-family: 'Roboto', sans-serif;
    }
    .stTextArea > div > textarea {
        border: 1px solid #ccc;
        border-radius: 5px;
        font-family: 'Roboto', sans-serif;
    }
    .submit-button {
        display: flex;
        justify-content: center;
    }
    .submit-button .stButton > button {
        background-color: #4fb8ac;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        width: 200px;
        font-family: 'Roboto', sans-serif;
    }
    .kyra-favicon-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 18px;
        margin-top: 10px;
    }
    .kyra-favicon-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        box-shadow: 0 4px 24px #4fb8ac55, 0 0 0 8px #fff;
        border: 5px solid #4fb8ac;
        background: #fff;
        display: block;
    }
    .kyra-logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 80px;
    }
    .history-entry {
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        background-color: #ffffff;
        margin-bottom: 10px;
        box-shadow: 1px 1px 3px #ccc;
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Ky’ra favicon/icon at the top (large, bold, beautiful) ---
st.markdown(
    f"""
    <div class="kyra-favicon-container">
        <img src="{kyra_icon_dataurl}" class="kyra-favicon-img" alt="Ky’ra Icon"/>
    </div>
    """,
    unsafe_allow_html=True
)

# Header with official Ky’ra logo
# Using the raw GitHub URL for the Ky’ra logo
try:
    logo_url = "https://raw.githubusercontent.com/SharmilaGhosh120/app16/main/WhatsApp%20Image%202025-05-20%20at%2015.17.59.jpeg"
    st.image(logo_url, width=80, caption="Ky’ra Logo", use_column_width="auto", output_format="JPEG")
except Exception as e:
    st.warning(f"Failed to load Ky’ra logo: {str(e)}. Please ensure the logo URL is accessible.")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input fields
st.subheader("Your Details")
email_input = st.text_input("Student Email", placeholder="student123@college.edu", help="Enter your college email address.")

# Personalized and role-based greeting with dashboards
if email_input:
    name = email_input.split('@')[0].capitalize() if '@' in email_input else "User"
    is_admin = "college" in email_input.lower()
    
    if is_admin:
        st.markdown(f"<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>🎓 Welcome College Admin, {name}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Manage student mappings, projects, and reports with Ky’ra.</p>", unsafe_allow_html=True)
        
        # Admin Dashboard: Student Mapping Upload
        st.subheader("Upload Student Mapping")
        uploaded_file = st.file_uploader("Upload a CSV file (student_id,project_title)", type=["csv"])
        if uploaded_file is not None:
            try:
                mapping_df = pd.read_csv(uploaded_file)
                required_columns = ["student_id", "project_title"]
                if not all(col in mapping_df.columns for col in required_columns):
                    st.error("CSV must contain 'student_id' and 'project_title' columns.")
                else:
                    st.markdown("**Preview of Uploaded Student Mapping:**")
                    st.dataframe(mapping_df)
                    if st.button("Save Mapping"):
                        # Append to projects.csv
                        mapping_df["Timestamp"] = datetime.now().strftime("%d-%m-%Y %H:%M")
                        existing_projects = pd.read_csv(PROJECTS_FILE) if os.path.exists(PROJECTS_FILE) else pd.DataFrame(columns=["student_id", "project_title", "Timestamp"])
                        updated_projects = pd.concat([existing_projects, mapping_df], ignore_index=True)
                        updated_projects.to_csv(PROJECTS_FILE, index=False)
                        st.success("Student mapping saved successfully!")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        st.markdown(f"<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>👋 Hi {name}, ready to explore your internship path?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Ask Ky’ra anything about resumes, interviews, or project help - I’ll guide you step-by-step!</p>", unsafe_allow_html=True)
        
        # Student Dashboard: Project Assignment Submission
        st.subheader("Submit Your Project Title")
        project_title = st.text_input("Enter your project title:", placeholder="E.g., AI-based Chatbot for Internship Assistance")
        if st.button("Submit Project"):
            if project_title:
                timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
                new_project = pd.DataFrame([[email_input, project_title, timestamp]], columns=["student_id", "project_title", "Timestamp"])
                existing_projects = pd.read_csv(PROJECTS_FILE) if os.path.exists(PROJECTS_FILE) else pd.DataFrame(columns=["student_id", "project_title", "Timestamp"])
                updated_projects = pd.concat([existing_projects, new_project], ignore_index=True)
                updated_projects.to_csv(PROJECTS_FILE, index=False)
                st.success("Project title submitted successfully!")
            else:
                st.error("Please enter a project title.")
else:
    st.markdown("<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>👋 Ask Ky’ra – Your Internship Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Hi! I’m Ky’ra, your internship buddy. Enter your email to get started!</p>", unsafe_allow_html=True)

# Query Section (for both roles)
if email_input:
    st.subheader("Ask Ky’ra a Question")
    sample_questions = [
        "How do I write my internship resume?",
        "What are the best final-year projects in AI?",
        "How can I prepare for my upcoming interview?",
        "What skills should I learn for a career in cybersecurity?"
    ]
    selected_question = st.selectbox("Choose a sample question or type your own:", sample_questions + ["Custom question..."])
    query_text = st.text_area("Your Question", value=selected_question if selected_question != "Custom question..." else "", height=150, placeholder="E.g., How can I prepare for my internship interview?")

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# Function to call Ky’ra's backend API
def kyra_response(email, query):
    api_url = "http://kyra.kyras.in:8000/student-query"
    payload = {"student_id": email.strip(), "query": query.strip()}
    try:
        response = requests.post(api_url, params=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response from Ky’ra.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API call failed: {str(e)}"

# Function to save queries to CSV (includes response)
def save_query(email, query, timestamp, response):
    new_row = pd.DataFrame([[email, query, timestamp, response]], columns=["student_id", "Query", "Timestamp", "response"])
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(CSV_FILE, index=False)

# Submit button logic for queries
if email_input:
    st.markdown('<div class="submit-button">', unsafe_allow_html=True)
    if st.button("Submit", type="primary"):
        if not email_input or not query_text:
            st.error("Please enter both a valid email and a query.")
        elif not is_valid_email(email_input):
            st.error("Please enter a valid email address (e.g., student@college.edu).")
        else:
            try:
                timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
                response = kyra_response(email_input, query_text)
                save_query(email_input, query_text, timestamp, response)
                st.session_state.chat_history.append({
                    "student_id": email_input,
                    "query": query_text,
                    "response": response,
                    "timestamp": timestamp
                })
                st.success("Thank you! Ky’ra has received your question and is preparing your guidance.")
                with st.expander("🧠 Ky’ra’s Response", expanded=True):
                    st.markdown(
                        f"""
                        <div style='background-color:#f0f8ff; padding:15px; border-radius:12px; box-shadow:1px 1px 3px #ccc; font-family: \"Roboto\", sans-serif;'>
                            <strong>Ky’ra’s Response:</strong><br>{response}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.error(f"Failed to process query: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Display chat history (filtered by user)
if email_input and os.path.exists(CSV_FILE):
    st.markdown("**🧾 Your Chat History:**")
    df = pd.read_csv(CSV_FILE)
    user_df = df[df['student_id'] == email_input]
    if not user_df.empty:
        for idx, row in user_df.iterrows():
            response_text = row['response'] if 'response' in row and pd.notna(row['response']) else "No response available."
            st.markdown(
                f"""
                <div class='history-entry'>
                    <strong>You asked:</strong> {row['Query']} <i>(submitted at {row['Timestamp']})</i><br>
                    <strong>Ky’ra replied:</strong> {response_text}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")
    else:
        st.markdown("<p style='font-family: \"Roboto\", sans-serif;'>No chat history yet. Ask Ky’ra a question to get started!</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Display project submissions (for students)
if email_input and not is_admin and os.path.exists(PROJECTS_FILE):
    st.subheader("Your Submitted Projects")
    projects_df = pd.read_csv(PROJECTS_FILE)
    user_projects = projects_df[projects_df['student_id'] == email_input]
    if not user_projects.empty:
        for idx, row in user_projects.iterrows():
            st.markdown(
                f"""
                <div class='history-entry'>
                    <strong>Project Title:</strong> {row['project_title']} <i>(submitted at {row['Timestamp']})</i>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")
    else:
        st.markdown("<p style='font-family: \"Roboto\", sans-serif;'>No projects submitted yet.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Storage notice
st.markdown("Your chat history and project submissions are securely stored to help Ky’ra guide you better next time.", unsafe_allow_html=True)

# Note: To match kyras.in theme, create .streamlit/config.toml with:
# [theme]
# base="light"
# primaryColor="#4fb8ac"
# backgroundColor="#ffffff"
# secondaryBackgroundColor="#f4f4f4"
# font="Roboto"

# TODO: For true backend integration, replace CSV storage with a database (e.g., PostgreSQL, MongoDB).
# Example: Use SQLAlchemy to connect to a database and store queries/projects.
# Example schema: queries(student_id, query, timestamp, response), projects(student_id, project_title, timestamp)
