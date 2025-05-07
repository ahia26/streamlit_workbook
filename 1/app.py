import streamlit as st

# Title and header
st.title("My First Streamlit App")
st.header("Basic Streamlit Components")

# Text description
st.write("This app demonstrates the basic usage of Streamlit.")

# Input fields
name = st.text_input("Enter your name:")
age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)

# Display output
if name:
    st.write(f"Hello, {name}!")
if age:
    st.write(f"You are {age} years old.")
