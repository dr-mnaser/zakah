#import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta
import os
from dotenv import load_dotenv  # pip install python-dotenv

# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")
# Load the environment variables
#DETA_KEY = st.secrets["DETA_KEY"]

# Initialize with a project key
deta = Deta(DETA_KEY)

#%%
# Income-Expenses database
# This is how to create/connect a database
db = deta.Base("zakah")


def insert_period(period, transaction, value, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": period, "transaction": transaction, "value": value, "comment": comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)

def delete_period(period):
    """If not found, the function will return None"""
    return db.delete(period)

def get_all_periods():
    items = fetch_all_periods()
    if len(items) > 0:
        periods = [item["key"] for item in items]
    else:
        periods = []
    return periods

#%%
# Users Authentication database
# This is how to create/connect a database
users_db = deta.Base("users")

def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return users_db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    """Returns a dict of all users"""
    res = users_db.fetch()
    return res.items


def get_user(username):
    """If not found, the function will return None"""
    return users_db.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return users_db.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return users_db.delete(username)

#%%
# # Students database
# # This is how to create/connect a database
# students_db = deta.Base("students")


# def insert_student(name, level, payment, date, comment):
#     """Returns the report on a successful creation, otherwise raises an error"""
#     return students_db.put({"key": name, "level": level, "payment": payment, "date": date, "comment": comment})


# def fetch_all_students():
#     """Returns a dict of all periods"""
#     res = students_db.fetch()
#     return res.items


# def get_student(name):
#     """If not found, the function will return None"""
#     return students_db.get(name)

# def delete_student(name):
#     """If not found, the function will return None"""
#     return students_db.delete(name)

# def get_all_students():
#     items = fetch_all_students()
#     if len(items) > 0:
#         names = [item["key"] for item in items]
#     else:
#         names = []
#     return names