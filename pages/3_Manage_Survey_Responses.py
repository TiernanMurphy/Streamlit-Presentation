import streamlit as st
import psycopg2
from datetime import datetime

st.title("📝 Manage Survey Responses")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

conn = get_connection()
cur = conn.cursor()

# Dynamic dropdowns
cur.execute("SELECT id, name FROM students ORDER BY name")
students = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT id, name FROM languages ORDER BY name")
languages = {row[1]: row[0] for row in cur.fetchall()}

# Add form
with st.form("add_response"):
    st.subheader("Record New Survey Response")
    student_name = st.selectbox("Student", options=list(students.keys()))
    lang_name = st.selectbox("Language", options=list(languages.keys()))
    proficiency = st.selectbox("Proficiency", ["Beginner", "Intermediate", "Expert"])
    exp_years = st.number_input("Years of Experience", min_value=0, value=1)
    submitted = st.form_submit_button("Record Response")

    if submitted:
        try:
            cur.execute("""
                INSERT INTO student_languages (student_id, language_id, proficiency, experience_years)
                VALUES (%s, %s, %s, %s)
            """, (students[student_name], languages[lang_name], proficiency, exp_years))
            conn.commit()
            st.success("Survey response recorded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Search/Filter table
search_term = st.text_input("Filter by student or language name")
if search_term:
    cur.execute("""
        SELECT sl.id, s.name, l.name, sl.proficiency, sl.experience_years, sl.survey_date
        FROM student_languages sl
        JOIN students s ON sl.student_id = s.id
        JOIN languages l ON sl.language_id = l.id
        WHERE s.name ILIKE %s OR l.name ILIKE %s
        ORDER BY sl.survey_date DESC
    """, (f"%{search_term}%", f"%{search_term}%"))
else:
    cur.execute("""
        SELECT sl.id, s.name, l.name, sl.proficiency, sl.experience_years, sl.survey_date
        FROM student_languages sl
        JOIN students s ON sl.student_id = s.id
        JOIN languages l ON sl.language_id = l.id
        ORDER BY sl.survey_date DESC
    """)
rows = cur.fetchall()

for row in rows:
    st.write(f"{row[1]} — {row[2]} | {row[3]} | {row[4]} years | {row[5]}")
    col1, col2 = st.columns(2)
    if col1.button("Delete", key=f"del_resp_{row[0]}"):
        if st.checkbox("Confirm delete this response?", key=f"conf_{row[0]}"):
            cur.execute("DELETE FROM student_languages WHERE id = %s", (row[0],))
            conn.commit()
            st.success("Deleted!")
            st.rerun()

conn.close()