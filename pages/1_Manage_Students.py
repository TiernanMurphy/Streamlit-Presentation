import streamlit as st
import psycopg2
import re

st.title("👥 Manage Students")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

conn = get_connection()
cur = conn.cursor()

# === Add Form ===
with st.form("add_student"):
    st.subheader("Add New Student")
    name = st.text_input("Name *")
    email = st.text_input("Email *")
    major = st.text_input("Major")
    submitted = st.form_submit_button("Add Student")

    if submitted:
        errors = []
        if not name.strip(): errors.append("Name is required.")
        if not email.strip(): errors.append("Email is required.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                cur.execute(
                    "INSERT INTO students (name, email, major) VALUES (%s, %s, %s)",
                    (name.strip(), email.strip(), major.strip() or None)
                )
                conn.commit()
                st.success("Student added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error (likely duplicate email): {e}")

# === Search + Table ===
search = st.text_input("Search students by name")
if search:
    cur.execute("SELECT id, name, email, major, created_at FROM students WHERE name ILIKE %s ORDER BY name", (f"%{search}%",))
else:
    cur.execute("SELECT id, name, email, major, created_at FROM students ORDER BY name")
rows = cur.fetchall()

for row in rows:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.write(f"**{row[1]}** — {row[2]} | {row[3] or '—'}")
    with col2:
        if st.button("Edit", key=f"edit_{row[0]}"):
            st.session_state.edit_student = row
    with col3:
        if st.button("Delete", key=f"del_{row[0]}"):
            st.session_state.del_student = row[0]

# Edit form (in session state)
if "edit_student" in st.session_state:
    with st.form("edit_student_form"):
        st.subheader("Edit Student")
        eid = st.session_state.edit_student[0]
        ename = st.text_input("Name", st.session_state.edit_student[1])
        eemail = st.text_input("Email", st.session_state.edit_student[2])
        emajor = st.text_input("Major", st.session_state.edit_student[3] or "")
        if st.form_submit_button("Save Changes"):
            cur.execute("UPDATE students SET name=%s, email=%s, major=%s WHERE id=%s",
                        (ename, eemail, emajor or None, eid))
            conn.commit()
            st.success("Updated!")
            del st.session_state.edit_student
            st.rerun()

# Delete with confirmation
if "del_student" in st.session_state:
    st.warning(f"Delete student ID {st.session_state.del_student}? This will also delete all their survey responses.")
    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete"):
        cur.execute("DELETE FROM students WHERE id = %s", (st.session_state.del_student,))
        conn.commit()
        st.success("Deleted!")
        del st.session_state.del_student
        st.rerun()
    if col2.button("Cancel"):
        del st.session_state.del_student
        st.rerun()

conn.close()