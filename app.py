import streamlit as st
import pandas as pd

from agent import generate_sql, generate_answer, is_safe_sql
from db import execute_query, set_database, get_db_type
from charts import create_chart


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI SQL Assistant", layout="wide")
st.title("🤖 AI SQL Assistant")


# =========================
# SESSION STATE
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

if "selected" not in st.session_state:
    st.session_state.selected = None

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if "show_db_panel" not in st.session_state:
    st.session_state.show_db_panel = True


# =========================
# SIDEBAR (HISTORY ONLY)
# =========================
st.sidebar.title("📜 History")

for i, item in enumerate(st.session_state.history):

    if st.sidebar.button(item["question"], key=f"btn_{i}"):
        st.session_state.selected = item


# =========================
# DB TOGGLE BUTTON
# =========================
if st.session_state.db_connected:
    if st.button("⚙️ Change database"):
        st.session_state.show_db_panel = True


# =========================
# DB PANEL (FORM FIXED)
# =========================
if not st.session_state.db_connected or st.session_state.show_db_panel:

    st.subheader("🔌 Database Connection")

    db_type = st.selectbox(
        "Choose database type",
        ["sqlite", "mysql", "postgres"],
        index=None,
        placeholder="Select a database type"
    )

    if db_type:

        # ================= SQLITE =================
        if db_type == "sqlite":

            with st.form("sqlite_form"):

                path = st.text_input("SQLite file", "Chinook_Sqlite.sqlite")
                submitted = st.form_submit_button("Connect SQLite")

                if submitted:

                    set_database("sqlite", path=path)

                    st.session_state.db_connected = True
                    st.session_state.show_db_panel = False
                    st.session_state.history = []
                    st.session_state.selected = None

                    st.success("Connected to SQLite")
                    st.rerun()


        # ================= MYSQL =================
        elif db_type == "mysql":

            with st.form("mysql_form"):

                host = st.text_input("Host", "localhost")
                port = st.text_input("Port", "3306")
                user = st.text_input("User", "root")
                password = st.text_input("Password", type="password")
                database = st.text_input("Database")

                submitted = st.form_submit_button("Connect MySQL")

                if submitted:

                    set_database(
                        "mysql",
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database
                    )

                    st.session_state.db_connected = True
                    st.session_state.show_db_panel = False
                    st.session_state.history = []
                    st.session_state.selected = None

                    st.success("Connected to MySQL")
                    st.rerun()


        # ================= POSTGRES =================
        elif db_type == "postgres":

            with st.form("postgres_form"):

                host = st.text_input("Host", "localhost")
                port = st.text_input("Port", "5432")
                user = st.text_input("User", "postgres")
                password = st.text_input("Password", type="password")
                database = st.text_input("Database")

                submitted = st.form_submit_button("Connect PostgreSQL")

                if submitted:

                    set_database(
                        "postgres",
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database
                    )

                    st.session_state.db_connected = True
                    st.session_state.show_db_panel = False
                    st.session_state.history = []
                    st.session_state.selected = None

                    st.success("Connected to PostgreSQL")
                    st.rerun()


# =========================
# BLOCK IF NOT CONNECTED
# =========================
if not st.session_state.db_connected:
    st.info("👉 Please connect to a database to start querying.")
    st.stop()


# =========================
# INPUT (TOP OF PAGE)
# =========================
question = st.text_input("Ask your database")


# =========================
# QUERY PIPELINE
# =========================
if st.button("Run Query") and question:

    st.session_state.selected = None

    sql = generate_sql(question)

    if sql is None:
        st.error("❌ Cette information n'existe pas dans la base de données.")

    else:

        st.subheader("SQL Generated")
        st.code(sql, language="sql")

        try:

            if not is_safe_sql(sql):
                st.error("❌ Unsafe SQL detected.")

            else:

                columns, rows = execute_query(sql)
                df = pd.DataFrame(rows, columns=columns)

                st.subheader("Answer")
                answer = generate_answer(question, sql, df)
                st.write(answer)

                st.subheader("Data")
                st.dataframe(df)

                fig = create_chart(df)

                if fig:
                    st.subheader("Chart")
                    st.plotly_chart(fig, use_container_width=True)

                st.session_state.history.append({
                    "question": question,
                    "sql": sql,
                    "answer": answer,
                    "df": df,
                    "fig": fig
                })

        except Exception as e:
            st.error(f"SQL Error: {e}")


# =========================
# HISTORY DISPLAY
# =========================
if st.session_state.selected is not None:

    item = st.session_state.selected

    st.subheader("SQL")
    st.code(item["sql"], language="sql")

    st.subheader("Answer")
    st.write(item["answer"])

    st.subheader("Data")
    st.dataframe(item["df"])

    if item["fig"] is not None:
        st.subheader("Chart")
        st.plotly_chart(item["fig"], use_container_width=True)