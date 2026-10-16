# MediAssist AI

MediAssist AI is a Streamlit chat app for general health education. It sends chat prompts to the Ollama service running on your own computer and uses the `gemma3` model. It does not need a cloud API key.

## What it can help explain

- General health and healthy-lifestyle topics
- Medical terms and basic health concepts
- General information about health services

It is not a diagnostic or treatment tool. It cannot diagnose, prescribe medication, or replace a qualified healthcare professional. For personal concerns, ask a healthcare professional. If you may be experiencing an emergency, contact your local emergency services promptly instead of waiting for an AI response.

## Privacy

Do not enter names, addresses, dates of birth, contact details, or other identifying patient information. The app sends prompts only to `http://localhost:11434/api/chat`; it does not call an external AI service. Chat history is kept in the running Streamlit session's memory and is not written to a database or file. Clearing the chat removes the visible session history.

## Requirements

- Windows 10 or newer
- Python 3.9 or newer
- Ollama for Windows
- The Ollama `gemma3` model

## Setup and run (PowerShell)

Open PowerShell in the project folder, then create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Install the Python dependency:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Ollama from [ollama.com](https://ollama.com), start the Ollama app, and download the model in a terminal:

```powershell
ollama pull gemma3
ollama list
```

Start MediAssist AI from the project folder:

```powershell
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`; open it in your browser. Keep the Ollama app running while you use MediAssist AI.

## Test the setup

Check Python syntax for the Streamlit app and both command-line scripts:

```powershell
python -m py_compile app.py medo.py medo2.0.py
```

Check that the model can respond directly through Ollama:

```powershell
ollama run gemma3
```

Type a general question, then enter `/bye` to exit. After that, run `streamlit run app.py` and confirm the sidebar reports Ollama and Gemma as ready. Try a suggested question, send a chat prompt, and use **Clear chat**.

## Troubleshooting

- **Ollama is not responding:** Start the Ollama desktop app, then try again. The local API should be available at `http://localhost:11434`.
- **Gemma is missing:** Run `ollama pull gemma3`, then refresh the MediAssist page.
- **The model reply times out:** The first response can take longer while Gemma loads. Retry after it has warmed up, or close other applications using substantial memory.
- **Streamlit is not recognized:** Activate the virtual environment again and run `python -m streamlit run app.py`.
- **PowerShell blocks venv activation:** Use the Command Prompt activation command above, then run the same install and launch commands.

## Project files

- `app.py`: Streamlit interface, local Ollama connection, safety notices, and session-only chat.
- `medo.py` and `medo2.0.py`: Existing command-line versions of the assistant.
- `requirements.txt`: Python packages needed for the Streamlit app.
