#import calendar  # Core Python Module
#from datetime import datetime  # Core Python Module
import datetime
#import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
import database as db  # local import
import pandas as pd
import streamlit_authenticator as stauth
import psutil
import math

# -------------- SETTINGS --------------
page_title = "Zakah Tracker"
page_icon = ":money_with_wings:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
# years = [datetime.today().year, datetime.today().year + 1]
# months = list(calendar.month_name[1:])

# Get today's date
today = datetime.date.today()

# Calculate 6 months before
six_months_ago = today - datetime.timedelta(days=365-11)

if 'start_date' not in st.session_state:
    st.session_state['start_date'] = six_months_ago
    
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = today
    
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
    
if 'transactions_changed' not in st.session_state:
    st.session_state['transactions_changed'] = True
    
    
       
# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Define a function to get the current CPU and memory usage of the system
def get_system_usage():
    cpu_percent = psutil.cpu_percent()
    mem_percent = psutil.virtual_memory().percent
    return cpu_percent, mem_percent

# Define a function to check if the app can serve a new user based on the current resource usage
def can_serve_user():
    cpu_percent, mem_percent = get_system_usage()
    # Check if the current CPU and memory usage are below the threshold
    if cpu_percent < 80 and mem_percent < 80:
        return True
    else:
        return False

def main():
# Check if the app can serve a new user
    if can_serve_user():    
        # -------------- SETTINGS --------------
        transactions = ["Income", "Expense"]
        currency = "USD"
        # --------------------------------------
        # --- NAVIGATION MENU ---
        selected = option_menu(
            menu_title=None,
            options=["Add", "Delete", "Visualization"],
            icons=["pencil-fill", "trash-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
            orientation="horizontal", default_index=2,
        )
        
        #fetch_all_periods()
        
        # --- INPUT & SAVE PERIODS ---
        if selected == "Add":
            st.header(f"Add Entry in {currency}")
            with st.form("entry_form", clear_on_submit=True):
                # Enter transaction name
                name = st.text_input("Enter Transaction Name", max_chars=50)
                "---"
                # Create date picker with default values
                period = st.date_input('Date', today)
                "---"
                transaction = option_menu(
                    menu_title=None,
                    options=transactions,
                    icons=["bank", "cash-coin"],  # https://icons.getbootstrap.com/
                    orientation="horizontal", default_index=1,
                )
                "---"
                value = st.number_input("Value", min_value=0, format="%i", step=10)
                    
                
                "---"
                #with st.expander("Comment"):
                comment = st.text_area("", placeholder="Enter a comment here ...")    
        
                "---"
                submitted = st.form_submit_button("Save Data")
        
                if submitted:
                    if not name:
                        st.error("Please enter a non-empty transaction name")
                    else:
                        try:
                            db.insert_period(name, str(period), transaction, value, comment)
                            st.session_state['transactions_changed'] = True
                            st.success("Data saved!")
                        except Exception as e:
                            st.write(f"Error: {e}")
                            st.write("Please try again!")
        
        # --- Delete Entry ---
        if selected == "Delete":
            st.header("Delete Entry")
            with st.form("delete_period"):
                if st.session_state['transactions_changed']:
                    try:
                        all_periods = db.get_all_periods()
                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.write("Please try again!")
                        all_periods = []
                else:
                    all_periods = [item['key'] for item in st.session_state['transactions']]
                    
                period = st.selectbox("Select Transaction:", all_periods)
                submitted = st.form_submit_button("Delete Entry")
                if submitted:
                    # Get data from database
                    if period is not None:
                        try:
                            db.delete_period(period)
                            st.session_state['transactions_changed'] = True
                            st.success("Data deleted!")
                        except Exception as e:
                            st.write(f"Error: {e}")
                            st.write("Please try again!")
                    
        # --- PLOT PERIODS ---
        if selected == "Visualization":
            st.header("Data Visualization")
            with st.form("saved_periods"):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input('Start date', st.session_state['start_date'])
                    st.session_state['start_date'] = start_date
                with col2:
                    end_date = st.date_input('End date', st.session_state['end_date'])
                    st.session_state['end_date'] = end_date
                
                "---"
                
                submitted = st.form_submit_button("Show Data")
                
                if submitted:
                    try:
                        if st.session_state['transactions_changed']:
                            items = db.fetch_all_periods()
                            st.session_state['transactions'] = items
                            st.session_state['transactions_changed'] = False
                        else:
                            items = st.session_state['transactions']
                        if len(items) > 0:
                            names = [item["key"] for item in items]
                            dates = [item["date"] for item in items]
                            transactions = [item["transaction"] for item in items]
                            values = [item["value"] for item in items]
                            comments = [item["comment"] for item in items]
                        else:
                            dates = []
                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.write("Please try again!")
                        dates = []
                        
                    if len(dates) > 0:
                        trans_names = []
                        trans_dates = []
                        trans_transactions = []
                        trans_values = []
                        trans_comments = []
                        for n, date_str in enumerate(dates):
                            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            if (date >= start_date) and (date <= end_date):
                                trans_names.append(names[n])
                                trans_dates.append(date_str)
                                trans_transactions.append(transactions[n])
                                trans_values.append(values[n])
                                trans_comments.append(comments[n])
                        data = {'Name': trans_names,'Date':trans_dates, 'Transaction':trans_transactions,
                                'Value':trans_values, 'Comments':trans_comments}
                        df = pd.DataFrame.from_dict(data)
                        
                        col4, col5, col6, col7 = st.columns(4)
                        total_income = 0
                        total_expense = 0
                        remaining_budget = 0
                        
                        total_income = sum(df[df['Transaction']=='Income']['Value'])
                        zakah = math.ceil(0.025 * total_income)
                        total_expense = sum(df[df['Transaction']=='Expense']['Value'])
                        remaining_budget = zakah - total_expense
                        col4.metric("Total Balance", f"${total_income}")
                        col5.metric("Zakah", f"${zakah}")
                        col6.metric("Paid", f"${total_expense}")
                        col7.metric("Remaining Zakah", f"${remaining_budget}")
                        
                        st.write(df)
                    else:
                        placeholder = st.empty()
                        placeholder.info("No Transactions available!")
    
    else:
        st.write("Sorry, the app is currently overloaded. Please try again later.")
    
# --- USER AUTHENTICATION ---  
@st.cache_data
def load_all_users():
    users = db.fetch_all_users()
    return users
users = load_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

credentials = {"usernames": {}}

for i in range(len(usernames)):
    credentials["usernames"][usernames[i]] = {"name": names[i], "password": hashed_passwords[i]}

authenticator = stauth.Authenticate(credentials, "app_home", "auth", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if 'name' not in st.session_state:
    st.session_state['name'] = name
    
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = authentication_status
    
if 'username' not in st.session_state['username']:
    st.session_state['username'] = username

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    #placeholder.empty()
    authenticator.logout("Logout", "main")
    
    main()