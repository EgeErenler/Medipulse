# MediPulse AI

An AI health assistant for people in the UK. You describe your symptoms in plain language, and Florence, the assistant, gives NHS-style guidance and points you to the right service: 999, NHS 111, your GP or a pharmacist.

**Live app:** [medipulse-ai.streamlit.app](https://medipulse-ai.streamlit.app)

## What it does

- Chat-based triage in warm, plain UK English
- Safety rules on every reply: emergencies go to 999, urgent cases to NHS 111, mental health crises to Samaritans (116 123)
- Never diagnoses or prescribes; always signposts to NHS services
- Collects a short profile (name, age, gender, existing conditions) one question at a time to make answers more relevant
- Offline fallback answers for key topics if the AI service is unavailable

## Built with

- Python
- Streamlit
- Google Gemini (`gemini-2.0-flash`) through the `google-genai` SDK

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Google API key in the sidebar when the app opens.

## Disclaimer

MediPulse AI is a portfolio project. It does not give medical advice and does not replace a doctor. In an emergency, call 999.

## Author

Built by **Ege Erenler**, software engineer and data scientist in London.
Portfolio: [egeerenler.com](https://egeerenler.com) · GitHub: [@EgeErenler](https://github.com/EgeErenler)
