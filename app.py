import streamlit as st
from dotenv import load_dotenv
from utils import *
import uuid

# Creating session variables
if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] = ''

def main():
    # Load environment variables
    load_dotenv()

    # Configure page settings
    st.set_page_config(page_title="Resume Screening Assistance")
    st.title("HR - Resume Screening Assistance 💁")
    st.subheader("I can help you in the resume screening process")

    # Input for job description
    job_description = st.text_area("Please paste the 'JOB DESCRIPTION' here...", key="1")

    # Input for number of resumes to return
    document_count = st.text_input("No. of 'RESUMES' to return", key="2")

    # File uploader for resumes (PDF files only)
    pdf_files = st.file_uploader("Upload resumes here, only PDF files allowed", type=["pdf"], accept_multiple_files=True)

    # Submit button
    submit = st.button("Help me with the analysis")

    if submit:
        # Validate inputs
        if not job_description or not document_count or not pdf_files:
            st.error("Please provide the job description, number of resumes, and upload PDF files.")
        elif not document_count.isdigit() or int(document_count) <= 0:
            st.error("Please enter a valid positive number for the 'No. of RESUMES' to return.")
        else:
            with st.spinner('Wait for it...'):
                # Generate a unique ID for this session to identify user-specific data
                st.session_state['unique_id'] = uuid.uuid4().hex

                # Create a list of documents from the uploaded PDF files
                final_docs_list = create_docs(pdf_files, st.session_state['unique_id'])

                # Display the number of resumes uploaded
                st.write(f"*Resumes uploaded*: {len(final_docs_list)}")

                # Create an embeddings instance
                embeddings = create_embeddings_load_data()

                # Push data to Pinecone (Make sure your Pinecone API key and environment are correct)
                pinecone_api_key = "Please replace your Pinecone API Key "
                pinecone_environment = "gcp-starter"
                pinecone_index_name = "test"

                push_to_pinecone(pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings, final_docs_list)

                # Fetch relevant documents from Pinecone
                relevant_docs = similar_docs(
                    job_description,
                    document_count,
                    pinecone_api_key,
                    pinecone_environment,
                    pinecone_index_name,
                    embeddings,
                    st.session_state['unique_id']
                )

                # Line separator for better UI organization
                st.write(":heavy_minus_sign:" * 30)

                # Display relevant documents on the UI
                if relevant_docs:
                    for idx, doc in enumerate(relevant_docs):
                        st.subheader(f"👉 {idx + 1}")

                        # Display document metadata
                        st.write(f"**File**: {doc[0].metadata['name']}")

                        # Expander for showing more information
                        with st.expander('Show me 👀'):
                            st.info(f"**Match Score**: {doc[1]}")
                            # Retrieve the summary of the current document
                            summary = get_summary(doc[0])
                            st.write(f"**Summary**: {summary}")
                else:
                    st.warning("No relevant documents found.")

        st.success("Hope I was able to save your time ❤️")

# Invoking main function
if __name__ == '__main__':
    main()
