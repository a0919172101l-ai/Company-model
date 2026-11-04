# Lyla 2.0 — Local NLP Company Assistant

## What this version does

1. Reads company knowledge records from `data/company_data.json`.
2. Encodes each company record and each user question with the local
   Sentence Transformers model `sentence-transformers/all-MiniLM-L6-v2`.
3. Uses cosine similarity to retrieve relevant records.
4. Ranks source sentences against the user's actual question.
5. Displays evidence-based sentences and the retrieved sources.
6. Refuses to guess when the knowledge base does not contain relevant information.

## Important limitations

- This project does **not** call OpenAI, Gemini, Claude, or another generative AI API.
- It does not contain a fixed list of customer questions and answers.
- It is a semantic search and extractive-answer system, not a generative chatbot.
  The answer sentences are taken from your approved company data.
- The pretrained model is downloaded the first time it runs. This is a model-file
  download, not an API call. On Streamlit Community Cloud, internet access is
  needed during setup/model download. If your teacher requires no internet
  connection at all, download and bundle the model files separately and change
  the model loading path.
- Similarity scores are not proof that an answer is correct. Test the system
  with known questions and unknown questions, and adjust the threshold.

## 1. Replace the sample data

Open `data/company_data.json`. Replace every sample record with facts approved
by your team. Each record has:

- `title`: short document title
- `category`: topic such as Services, Customers, Business Model, Technology
- `content`: factual information in natural language
- `source`: where the information came from (team document, approved report, etc.)

You may add as many records as needed. Keep each record focused on one topic.
Do not add unsupported claims, invented revenue, or unapproved forecasts.

Example structure:

```json
[
  {
    "title": "Service description",
    "category": "Services",
    "content": "Write the verified service information here.",
    "source": "Approved service plan"
  }
]
```

## 2. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The first run downloads the model files. It may take a little time.

## 3. Deploy to Streamlit Community Cloud

1. Upload `app.py`, `requirements.txt`, and the `data` folder to your GitHub repository.
2. Open Streamlit Community Cloud and choose **New app**.
3. Select your repository and branch.
4. Set **Main file path** to `app.py`.
5. Deploy.

## 4. Test the model

Use different ways to ask about a fact that is actually present in your data.
For example, if your data contains an approved revenue-model description, test:
- "How does the company earn money?"
- "Where does the company's income come from?"
- "What is the business's revenue model?"

Also test an unsupported question, such as:
- "What will the company's revenue be in 2030?"

Expected behavior: if the information is absent, Lyla should say it cannot find
sufficient information instead of inventing an answer.

## 5. Explain the system to your teacher

"Lyla does not use a generative AI API or a manually written question-answer
list. It uses a pretrained Sentence Transformers model locally to convert the
user's question and our company documents into semantic vectors. It compares
them with cosine similarity, retrieves the most relevant company information,
and displays source sentences as an evidence-based response. If the knowledge
base does not contain relevant information, it refuses to guess."

## Troubleshooting

- **Model download error:** check that the deployment environment can access
  Hugging Face during the first model download.
- **Slow first launch:** normal; model files need to be downloaded and loaded.
- **Wrong records retrieved:** improve the clarity and organization of company
  records, add missing approved information, and test the similarity threshold.
- **No answer for a valid question:** the threshold may be too high. Test lower
  values such as `0.24` in `app.py`; do not lower it blindly.
