# LYLA Company AI (No API)

A Streamlit prototype for the LYLA semiconductor/AI company exhibition. It uses prepared company information and keyword matching; it does not call OpenAI, Groq, or another external AI API.

## Features

- Company Q&A for investors and exhibition visitors
- Proposed AI service catalog
- 25 test questions
- Clear response when information is not available
- Example pricing clearly labelled as a student business-model assumption
- Streamlit web interface suitable for GitHub + Streamlit Community Cloud

## Important limitation

This is a **rule-based information assistant**, not a generative AI model. It does not train itself or inspect uploaded product images. AI defect detection would require a separate image-classification model trained and tested with labelled normal/defective images.

## Run locally

1. Install Python.
2. Open a terminal in this project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy with GitHub and Streamlit Community Cloud

1. Create a GitHub repository, for example `lyla-company-ai`.
2. Upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore`.
3. Open Streamlit Community Cloud and connect your GitHub account.
4. Choose the repository and branch `main`.
5. Set the main file path to `app.py`.
6. Deploy. No API key or Streamlit Secrets are required.

## Project assumptions

Any price shown in the app is a student business-model assumption, not a market-verified price. The project does not claim confirmed customers, profits, or commercial model performance.
