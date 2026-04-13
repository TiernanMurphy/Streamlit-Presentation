import streamlit as st
import psycopg2
import re

st.title("🗣️ Manage Programming Languages")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

conn = get_connection()
cur = conn.cursor()

# ====================== ADD NEW LANGUAGE ======================
with st.form("add_language"):
    st.subheader("Add New Programming Language")
    name = st.text_input("Language Name *")
    paradigm = st.selectbox("Paradigm", 
                            ["Multi-paradigm", "Functional", "Object-Oriented", 
                             "Systems", "Scripting", "Procedural"])
    year_created = st.number_input("Year Created", min_value=1950, max_value=2030, value=2000)
    submitted = st.form_submit_button("Add Language")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Language Name is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                cur.execute(
                    "INSERT INTO languages (name, paradigm, year_created) VALUES (%s, %s, %s)",
                    (name.strip(), paradigm, int(year_created))
                )
                conn.commit()
                st.success(f"✅ Language '{name}' added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error (possible duplicate name): {e}")

# ====================== SEARCH + TABLE ======================
search = st.text_input("Search languages by name")

if search.strip():
    cur.execute("""
        SELECT id, name, paradigm, year_created 
        FROM languages 
        WHERE name ILIKE %s 
        ORDER BY name
    """, (f"%{search.strip()}%",))
else:
    cur.execute("""
        SELECT id, name, paradigm, year_created 
        FROM languages 
        ORDER BY name
    """)

rows = cur.fetchall()

st.subheader("Current Languages")

for row in rows:
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.write(f"**{row[1]}** — {row[2]} ({row[3]})")
    with col2:
        if st.button("Edit", key=f"edit_lang_{row[0]}"):
            st.session_state.edit_language = row
    with col3:
        if st.button("Delete", key=f"del_lang_{row[0]}"):
            st.session_state.del_language = row[0]

# ====================== EDIT FORM ======================
if "edit_language" in st.session_state:
    with st.form("edit_language_form"):
        st.subheader("Edit Language")
        row = st.session_state.edit_language
        eid = row[0]
        ename = st.text_input("Language Name", row[1])
        eparadigm = st.selectbox("Paradigm", 
                                 ["Multi-paradigm", "Functional", "Object-Oriented", 
                                  "Systems", "Scripting", "Procedural"], 
                                 index=["Multi-paradigm", "Functional", "Object-Oriented", 
                                        "Systems", "Scripting", "Procedural"].index(row[2]) 
                                 if row[2] in ["Multi-paradigm", "Functional", "Object-Oriented", 
                                               "Systems", "Scripting", "Procedural"] else 0)
        eyear = st.number_input("Year Created", min_value=1950, max_value=2030, value=row[3] or 2000)
        
        if st.form_submit_button("Save Changes"):
            try:
                cur.execute(
                    "UPDATE languages SET name=%s, paradigm=%s, year_created=%s WHERE id=%s",
                    (ename.strip(), eparadigm, int(eyear), eid)
                )
                conn.commit()
                st.success("Language updated successfully!")
                del st.session_state.edit_language
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

# ====================== DELETE WITH CONFIRMATION ======================
if "del_language" in st.session_state:
    st.warning(f"⚠️ Delete language ID {st.session_state.del_language}? "
               "This will also delete all survey responses linked to this language.")
    
    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete Permanently", type="primary"):
        try:
            cur.execute("DELETE FROM languages WHERE id = %s", (st.session_state.del_language,))
            conn.commit()
            st.success("Language and related responses deleted.")
            del st.session_state.del_language
            st.rerun()
        except Exception as e:
            st.error(f"Delete failed: {e}")
    
    if col2.button("Cancel"):
        del st.session_state.del_language
        st.rerun()

conn.close()