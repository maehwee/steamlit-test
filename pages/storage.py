import streamlit as st
import hmac
from st_files_connection import FilesConnection

import pandas as pd
import s3fs

st.title("Messages")

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here

# Actual messages
# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
df = conn.read("streamlitbucket2/myfile.csv", input_format="csv", ttl=600)

# Print results.
for row in df.itertuples():
    st.write(f"{row.Name} said \"{row.Message}\"")


# Writing to file
# Initialize S3 filesystem
fs = s3fs.S3FileSystem(anon=False)

# Streamlit app
st.title("Send a message")

# Input fields
name = st.text_input("Enter your name")
message = st.text_input("Enter your message")

if st.button("Submit"):
    if name and message:
        # S3 bucket and file details
        bucket_name = "streamlitbucket2"
        file_name = "myfile.csv"
        s3_path = f"{bucket_name}/{file_name}"

        try:
            # Read existing CSV file
            with fs.open(s3_path, 'r') as f:
                df = pd.read_csv(f)
            
            # Append new data
            new_data = pd.DataFrame({'Name': [name], 'Message': [message]})
            df = pd.concat([df, new_data], ignore_index=True)
            
            # Write updated dataframe back to S3
            with fs.open(s3_path, 'w') as f:
                df.to_csv(f, index=False)
            
            st.success("Data successfully added to the CSV file in S3!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter both name and message.")