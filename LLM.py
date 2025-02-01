import requests
import json
from tabulate import tabulate

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
