import streamlit as st
import LLM
import fitz  # PyMuPDF

def main():
    st.set_page_config(page_title="Interview Prep", layout="wide")
    st.title("Technical Interview Question Generator")
    
    # Initialize session state
    if 'main_questions' not in st.session_state:
        st.session_state.main_questions = []
    if 'followups' not in st.session_state:
        st.session_state.followups = {}
    if 'nested_followups' not in st.session_state:
        st.session_state.nested_followups = {}

    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    additional_prompt = st.text_input("Additional Prompt")

    # Main question generation
    if uploaded_file and additional_prompt:
        if st.button("Generate Initial Questions"):
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pdf_content = ""
            for page in pdf_document:
                pdf_content += page.get_text()
            st.session_state.main_questions = LLM.generate_questions(pdf_content, additional_prompt)

    # Display main questions as buttons
    if st.session_state.main_questions:
        st.header("Core Questions")
        cols = st.columns(3)
        for idx, question in enumerate(st.session_state.main_questions):
            with cols[idx % 3]:
                if st.button(question, key=f"q_{idx}"):
                    st.session_state.followups[question] = LLM.generate_followup_questions(question)

    # Display follow-up questions
    if st.session_state.followups:
        st.header("Follow-up Questions")
        for base_q, followups in st.session_state.followups.items():
            with st.expander(f"Follow-ups for: {base_q}"):
                f_cols = st.columns(3)
                for idx, fq in enumerate(followups):
                    with f_cols[idx % 3]:
                        if st.button(fq, key=f"f_{base_q}_{idx}"):
                            # Only generate nested follow-ups if they haven't been generated before
                            if fq not in st.session_state.nested_followups:
                                st.session_state.nested_followups[fq] = LLM.generate_nested_followup_questions(fq)

                # Display nested follow-up questions directly in the follow-up section
                for fq in followups:
                    if fq in st.session_state.nested_followups:
                        nested_followups = st.session_state.nested_followups[fq]
                        st.write(f"Nested Follow-ups for: {fq}")
                        for nested_q, nested_fqs in nested_followups.items():
                            st.write(f"- {nested_q}")
                            for n_fq in nested_fqs:
                                st.write(f"  - {n_fq}")

if __name__ == "__main__":
    main()
