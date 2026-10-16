import json
import urllib.request
import urllib.error
import urllib.request
import urllib.error

# ==========================================
# MEDICAL INFORMATION AI ASSISTANT
# Python + Ollama + Gemma
# ==========================================

MODEL = "gemma3"
API_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You are a Medical Information and Hospital Support AI Assistant.

Your responsibilities:
1. Explain general health topics in simple language.
2. Explain medical terminology.
3. Share general preventive healthcare information.
4. Explain the general purpose of medicines without prescribing.
5. Help users understand hospital departments and appointments.
6. Encourage users to consult qualified healthcare professionals.

IMPORTANT SAFETY RULES:
- You are NOT a doctor.
- Never claim to diagnose a disease.
- Never prescribe medicines or personalized dosages.
- Never tell users to start, stop, or change medication.
- Do not invent medical facts.
- If uncertain, clearly say so.
- For serious or worsening symptoms, recommend urgent medical care.
- For emergencies, tell the user to contact local emergency
  services immediately.
- Do not ask for names, passwords, addresses, or other
  unnecessary personal information.
- Do not claim to replace a doctor.
- Use clear, friendly, simple language.
"""

# Emergency warning keywords.
# These are simple safeguards, not a medical triage system.
EMERGENCY_KEYWORDS = [
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe chest pain",
    "unconscious",
    "not waking up",
    "severe bleeding",
    "face drooping",
    "sudden weakness",
    "stroke symptoms",
    "overdose",
    "severe allergic reaction"
]


def check_emergency(message):
    """Check for common emergency warning phrases."""
    message = message.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message:
            return True

    return False


def ask_ollama(question, history):
    """Send the question to the locally running Ollama model."""

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": question
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["message"]["content"]


def main():
    print("=" * 55)
    print("       MEDICAL INFORMATION AI ASSISTANT")
    print("             Powered by Ollama")
    print("=" * 55)

    print("\nHello! I can help with general health information,")
    print("medical terminology, preventive care, and hospital")
    print("questions.\n")

    print("IMPORTANT:")
    print("I am not a doctor and cannot diagnose or prescribe.")
    print("Do not enter identifiable patient information.")
    print("For emergencies, contact local emergency services.")
    print("\nType 'exit' to close the assistant.")
    print("-" * 55)

    history = []

    while True:
        question = input("\nYou: ").strip()

        if not question:
            continue

        if question.lower() in ["exit", "quit", "bye"]:
            print("\nAssistant: Take care! Consult a healthcare")
            print("professional for personal medical advice.")
            break

        # Basic emergency warning
        if check_emergency(question):
            print("\nEMERGENCY WARNING:")
            print(
                "Your message may describe a medical emergency. "
                "Do not wait for an AI response. Contact your "
                "local emergency number or go to the nearest "
                "emergency department immediately. Do not drive "
                "yourself if you may be seriously unwell."
            )

            # In a possible emergency, don't delay by waiting
            # for the AI model to respond.
            continue

        print("\nAssistant: Thinking...\n")

        try:
            answer = ask_ollama(question, history)
            print("Assistant:", answer)

            # Keep a limited conversation history.
            history.append({
                "role": "user",
                "content": question
            })

            history.append({
                "role": "assistant",
                "content": answer
            })

            history = history[-10:]

        except urllib.error.URLError:
            print("ERROR: Cannot connect to Ollama.")
            print("Please make sure Ollama is installed and running.")
            print("Then download the model using:")
            print("ollama pull gemma3")

        except urllib.error.HTTPError as error:
            print("Ollama returned an HTTP error:", error.code)
            print("Check that the model is installed:")
            print("ollama list")
            print("If necessary, run: ollama pull gemma3")

        except TimeoutError:
            print("The model took too long to respond.")
            print("Try again or use a smaller compatible model.")

        except (KeyError, ValueError, json.JSONDecodeError):
            print("Could not read the model response.")
            print("Please check that Ollama is working correctly.")

        except Exception as error:
            print("Unexpected error:", error)


if __name__ == "__main__":
    main()
