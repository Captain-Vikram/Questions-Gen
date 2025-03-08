import streamlit as st
import requests
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
import re
from flask_cors import CORS
import json  # Ensure this import is present
import re  # Ensure this import is present
from json import JSONDecodeError

app = Flask(__name__)

def get_models():
    url = "http://127.0.0.1:1234/v1/models"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.text}"

def chat_completion(prompt, model_name="meta-llama-3.1-8b-instruct", temperature=0.7, context=None):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    messages = context if context else []
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": -1,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"

def text_completion(prompt, model_name="meta-llama-3.1-8b-instruct", temperature=0.7):
    url = "http://127.0.0.1:1234/v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": -1,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["text"]
    else:
        return f"Error: {response.text}"

def text_embedding(text):
    url = "http://127.0.0.1:1234/v1/embeddings"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "text-embedding-nomic-embed-text-v1.5",
        "input": text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["data"][0]["embedding"]
    else:
        return f"Error: {response.text}"

def generate_questions(pdf_content, additional_prompt):
    """Generate initial interview questions based on PDF content and an additional prompt."""
    prompt = f"Generate 3 technical interview questions based on the following content: {pdf_content}. Additional prompt: {additional_prompt}. Return them as a list. and keep in mind on keep them concise to the point not confussing atall and witha max words of 20 in each of the question and also only generate the question and nothing around that!!! donot generate stuff like 'Here are three technical interview questions based on YashKolambekar's skills and experience:' and all, only the list of questions and nothing else"
    response = chat_completion(prompt)
    questions = [q.strip() for q in response.split('\n') if q.strip()]
    return questions[:3]  # Ensure we return exactly 3 questions

def generate_followup_questions(base_question):
    """Generate follow-up questions based on a given question."""
    prompt = f"Given this technical interview question: '{base_question}', generate 3 relevant follow-up questions that dig deeper into the topic. Return them as a list. and keep in mind on keep them concise to the point not confussing atall and witha max words of 20 in each of the question and also only generate the question and nothing around that!!! donot generate stuff like 'Here are three technical interview questions based on YashKolambekar's skills and experience:' and all, only the list of questions and nothing else"
    response = chat_completion(prompt)
    questions = [q.strip() for q in response.split('\n') if q.strip()]
    return questions[:3]  # Ensure we return exactly 3 follow-up questions

def generate_nested_followup_questions(base_question):
    """Generate nested follow-up questions for a given follow-up question."""
    followups = generate_followup_questions(base_question)
    nested_followups = {}
    for fq in followups:
        nested_followups[fq] = generate_followup_questions(fq)  # Generate additional follow-ups for each follow-up
    return nested_followups

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_content = ""
    for page in pdf_document:
        pdf_content += page.get_text()
    return pdf_content

def analyze_speech_and_score(speech_text):
    """Analyze the provided speech text and generate a score and review."""
    prompt = f"Analyze the following speech text: {speech_text} The speech txt might include repetition of some sentences and word it is because of the capturing process donot include it as a speakers repition or fault ignore that one aspect and analyze. Provide a score between 0 and 10 based on clarity, relevance, and technical depth. THE WHOLE REVIEW SHOULD BE ONLY 4 SMALL SENTENCES FOCUSING ON THE FINAL SCORE GENERATION AND NOTHING ELSE. Format your response as 'REVIEW: [your 4-sentence review] SCORE: [numerical score]'"
    
    response = chat_completion(prompt)

    try:
        response_json = json.loads(response) if isinstance(response, str) else response
        response_text = response_json["choices"][0]["message"]["content"].strip()
    except (JSONDecodeError, KeyError, TypeError):
        response_text = str(response).strip()

    # Extract review and score separately
    review_match = re.search(r"REVIEW:\s*(.*?)\s*SCORE:", response_text, re.DOTALL)
    review = review_match.group(1).strip() if review_match else "No review available."
    
    # Try to extract a numerical score from the response
    score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", response_text)
    if score_match:
        score = float(score_match.group(1))
        score = min(max(score, 0), 10)  # Clamp score between 0 and 10
    else:
        # Fallback to searching for any number if the format wasn't followed
        score_match = re.search(r"\b\d+(?:\.\d+)?\b", response_text)
        if score_match:
            score = float(score_match.group(0))
            score = min(max(score, 0), 10)
        else:
            score = 7.5  # Default score if no number is found
    
    return {"score": score, "review": review}

@app.route('/generate_questions', methods=['POST'])
def api_generate_questions():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400
    
    pdf_file = request.files['pdf_file']
    additional_prompt = request.form.get('additional_prompt', '')

    pdf_content = extract_text_from_pdf(pdf_file)

    if not pdf_content.strip():
        return jsonify({"error": "Empty or unreadable PDF content"}), 400

    questions = generate_questions(pdf_content, additional_prompt)
    return jsonify(questions)

@app.route('/generate_followup_questions', methods=['POST'])
def api_generate_followup_questions():
    data = request.json
    base_question = data.get('base_question')
    followup_questions = generate_followup_questions(base_question)
    return jsonify(followup_questions)

@app.route('/generate_nested_followup_questions', methods=['POST'])
def api_generate_nested_followup_questions():
    data = request.json
    base_question = data.get('base_question')
    nested_followup_questions = generate_nested_followup_questions(base_question)
    return jsonify(nested_followup_questions)

CORS(app)  # Enable CORS for all routes

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # For preflight OPTIONS requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    data = request.json
    speech_text = data.get('speech_text')
    if not speech_text:
        return jsonify({'error': 'Invalid input'}), 400

    result = analyze_speech_and_score(speech_text)
    return jsonify(result)  # Now returns both score and review

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
            st.session_state.main_questions = generate_questions(pdf_content, additional_prompt)

    # Display main questions as buttons
    if st.session_state.main_questions:
        st.header("Core Questions")
        cols = st.columns(3)
        for idx, question in enumerate(st.session_state.main_questions):
            with cols[idx % 3]:
                if st.button(question, key=f"q_{idx}"):
                    st.session_state.followups[question] = generate_followup_questions(question)

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
                                st.session_state.nested_followups[fq] = generate_nested_followup_questions(fq)

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
    app.run(port=5000)