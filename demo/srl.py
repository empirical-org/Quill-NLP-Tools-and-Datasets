import streamlit as st
import base64

from quillnlp.preprocessing.srl import perform_srl


st.sidebar.title("Quill NLP Tools")
st.sidebar.markdown(
    """
    SRL & Clustering
    """
)

st.title("Data Preprocessing")

st.write("Please enter the prompt and upload a txt file with one response per line.")

prompt = st.text_input("Prompt:", value="")

uploaded_file = st.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    with open(uploaded_file) as i:
        responses = [line.strip() for line in i]

    results = perform_srl(responses, prompt)
    result_string = "\n".join(["\t".join(item) for item in results])

    b64 = base64.b64encode(results.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download tab-separated file</a> (right-click and save as &lt;some_name&gt;.tsv)'
    st.markdown(href, unsafe_allow_html=True)
