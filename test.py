import streamlit as st
import pandas as pd
import numpy as np

# Title of the app
st.title('My First Streamlit App')

# Writing text
st.write('Here is some data and a chart.')

# Creating a DataFrame
data = pd.DataFrame({
    'col1': list(range(10)),
    'col2': np.random.randn(10)
})

# Displaying the DataFrame as a table
st.dataframe(data)

# Displaying a line chart
st.line_chart(data['col2'])