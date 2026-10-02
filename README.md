# Climate Information Bot

An English and Urdu chatbot that gives practical disaster-preparedness guidance for Chitral, Khyber Pakhtunkhwa, Pakistan. It answers from a set of safety guides and shows which guide each answer came from.

**Live app:** [https://climate-bot-q7grmfcxpqnrrbn5eyr9gk.streamlit.app/]

> This bot gives general preparedness guidance. It is not a live-alert or emergency service. In immediate danger, call **Rescue 1122**.

## The problem

Floods, earthquakes, heatwaves and glacier-lake outburst floods (GLOFs) are real risks in mountain regions like Chitral. People often do not know what to do before, during and after these events, and the information is scattered and not always available in Urdu or written for local conditions.

## What it does

- Answers preparedness questions in **English or Urdu**, in the language of the question.
- Covers **floods, earthquakes, heatwaves, emergency kits, and glaciers and GLOFs**.
- Shows the **source guide** under every answer for transparency.
- Offers one-click **topic buttons** and an area selector (Chitral, Upper Chitral, Lower Chitral, Khyber Pakhtunkhwa, Pakistan).
- Displays Urdu answers **right to left** in an Urdu font.
- Always shows the **Rescue 1122** emergency notice.
- Works on phones and computers.

## How it works

This project uses **RAG (Retrieval-Augmented Generation)**, so the AI answers from our guides and not only from what it learned in training.

```
User question
   -> converted to numbers (multilingual embedding)
   -> compared with pieces of the safety guides (cosine similarity)
   -> the 4 closest pieces are selected
   -> sent to the AI model together with the question
   -> answer returned with the source guide names
```

1. **Chunking:** each guide is split at its headings, and long sections are cut at about 1200 characters, so each piece covers one topic.
2. **Embeddings:** every piece is turned into a vector with a multilingual model, so an Urdu question can find the matching guide text.
3. **Retrieval:** the question is embedded the same way, and the 4 most similar pieces are chosen.
4. **Generation:** the pieces are placed in the prompt as context. The model is told to reply in the user's language, keep the answer short, use specific numbers only if they appear in the context, and refer people to Rescue 1122, PDMA and PMD when unsure.

## Tech stack

| Part | Technology |
|---|---|
| Interface | Streamlit (custom CSS, Urdu right-to-left support) |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` through `fastembed` (ONNX) |
| Search | NumPy cosine similarity, top 4 pieces |
| Language model | `openai/gpt-oss-120b` on Groq, temperature 0.3 |
| Knowledge base | Markdown guides in English and Urdu |
| Hosting | GitHub and Streamlit Community Cloud |

The project began as two parts (a FastAPI backend with ChromaDB, and a Streamlit frontend). It was merged into a single lightweight app so it could run on free hosting.

## Project structure

```
app.py              Streamlit interface
rag.py              Retrieval and answer generation
requirements.txt    Python packages
data/               Safety guides (.md)
  floods_pk.md
  earthquake_pk.md
  heatwave_pk.md
  emergency_kit.md
  glaciers_glof_pk.md
```

## Run it locally

You need Python 3 and a free [Groq API key](https://console.groq.com/keys).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the file `.streamlit/secrets.toml` with your key:

```toml
GROQ_API_KEY = "your_key_here"
```

Then start the app:

```powershell
python -m streamlit run app.py
```

The first start downloads the embedding model, so it takes a minute.

## Deploy

1. Pushed `app.py`, `rag.py`, `requirements.txt` and the guides to a GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), created an app from the repository with `app.py` as the main file.
3. Under **Advanced settings > Secrets**, added `GROQ_API_KEY = "your_key_here"`.

Never committed key. `.streamlit/secrets.toml` and `.env` they should stay out of GitHub.

## Limitations

- It provides general guidance and does not read live alerts or weather data.
- The language model can still add details that are not in the guides, so the guides should be checked against official sources (NDMA, PDMA, PMD).
- Each question is answered independently, and the bot does not remember earlier messages.
- Most guides cover Pakistan in general. Only the glacier and GLOF guide is written for Chitral, and the area selector changes the prompt wording and not which guides are searched.
- Answer quality in Urdu depends on the language model.
- The free host puts the app to sleep, so the first load can be slow.

## Future work

- Local languages such as Khowar.
- Real-time alerts from PMD and PDMA.
- More hazards: landslides, cloudbursts and cold waves.
- A household risk profile that creates a personal preparedness plan.
- Conversation memory and a minimum-relevance check, so the bot says clearly when a topic is not covered.
- A formal accuracy test with a larger question set.

## Screenshots

<img width="1351" height="595" alt="home" src="https://github.com/user-attachments/assets/f097ca6b-69da-4c74-a5dc-3a5711099438" />
<img width="1355" height="586" alt="english-answer-1" src="https://github.com/user-attachments/assets/cab7c128-43d6-4fb0-8ad2-3a68740645ca" />
<img width="1340" height="567" alt="english-answer-2" src="https://github.com/user-attachments/assets/befaa5d7-8a62-4e46-93ab-434440f8ada7" />
<img width="1347" height="586" alt="urdu-answer" src="https://github.com/user-attachments/assets/70324e04-5316-432f-a2f1-e300f06d91e9" />



## Team

Simrah Tariq (03458916585), Kainat Saif, Syeda Ummi Atika, Adeela Haqqi
