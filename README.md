# Technical Interview Question Generator

This project is a web application that generates technical interview questions based on the content of a PDF file and an additional prompt. It uses a language model to generate initial questions, follow-up questions, and nested follow-up questions.

## Features

- Upload a PDF file and provide an additional prompt to generate initial interview questions.
- Generate follow-up questions based on the initial questions.
- Generate nested follow-up questions for deeper insights.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/interview-question-generator.git
    cd interview-question-generator
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    python new_ui.py
    ```

## Usage

1. Open the web application in your browser.
2. Upload a PDF file containing the content you want to generate questions from.
3. Provide an additional prompt to guide the question generation.
4. Click the "Generate Initial Questions" button to generate the questions.
5. Click on the generated questions to generate follow-up questions.
6. Click on the follow-up questions to generate nested follow-up questions.

## API Endpoints

- `POST /generate_questions`: Generate initial interview questions based on PDF content and an additional prompt.
- `POST /generate_followup_questions`: Generate follow-up questions based on a given question.
- `POST /generate_nested_followup_questions`: Generate nested follow-up questions for a given follow-up question.

## Dependencies

- Python 3.7+
- Streamlit
- Flask
- Requests
- PyMuPDF

## License

This project is licensed under the MIT License. See the LICENSE file for details.
