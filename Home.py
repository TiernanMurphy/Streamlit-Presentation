import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Programming Language Survey", layout="wide")
st.title("📊 Student Programming Language Survey Dashboard")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

conn = get_connection()

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    st.metric("Total Students", cur.fetchone()[0])

with col2:
    cur.execute("SELECT COUNT(*) FROM languages")
    st.metric("Total Languages", cur.fetchone()[0])

with col3:
    cur.execute("SELECT COUNT(*) FROM student_languages")
    st.metric("Total Survey Responses", cur.fetchone()[0])

with col4:
    cur.execute("""
        SELECT l.name, COUNT(*) 
        FROM student_languages sl 
        JOIN languages l ON sl.language_id = l.id 
        GROUP BY l.name 
        ORDER BY COUNT(*) DESC LIMIT 1
    """)
    top = cur.fetchone()
    st.metric("Most Popular Language", top[0] if top else "None")

st.subheader("Recent Survey Responses")
cur.execute("""
    SELECT s.name, l.name, sl.proficiency, sl.experience_years, sl.survey_date 
    FROM student_languages sl
    JOIN students s ON sl.student_id = s.id
    JOIN languages l ON sl.language_id = l.id
    ORDER BY sl.survey_date DESC LIMIT 10
""")
df = pd.DataFrame(cur.fetchall(), columns=["Student", "Language", "Proficiency", "Years Exp", "Survey Date"])
st.dataframe(df, use_container_width=True)

conn.close()