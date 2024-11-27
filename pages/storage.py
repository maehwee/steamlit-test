import streamlit as st
from st_files_connection import FilesConnection

import pandas as pd
import s3fs

st.title("Messages")
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