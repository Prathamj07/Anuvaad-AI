import os
import requests
import subprocess
import json

# ---------------------------
# 1️⃣ Set your API keys
# ---------------------------
GEMINI_API_KEY = "AIzaSyBqp2PwIV4QgLIjo73mKmt7vyb-D1HnkhA"
ELEVENLABS_API_KEY = "sk_b8c6c84322c3f2e6dc4242bab781a0e46aa5dd742f1b82a5"

if not GEMINI_API_KEY or not ELEVENLABS_API_KEY:
    exit("🚨 Please set both GEMINI_API_KEY and ELEVENLABS_API_KEY.")

# ElevenLabs Voice IDs
HOST_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
EXPERT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

# ---------------------------
# 2️⃣ Hardcoded article
# ---------------------------
article = """
Haryana cadre IPS officer Y Puran Kumar, 52, left an eight-page “final note”,
in which he named three retired IAS and 10 IPS officers and how they allegedly
“tortured him mentally and administratively” during his service-career.
The wife of the 2001-batch officer, Amneet P Kumar, meanwhile, returned from
Japan Wednesday and allegedly refused to get the post mortem examination,
“till justice is delivered”. The Indian Express confirmed it from three sources
who met Amneet Wednesday and confirmed that “although visibly shattered, she was
furiously angry and has refused to get the post mortem done till justice is delivered”.
"""


# ---------------------------
# 3️⃣ Generate podcast script using Gemini (latest model)
# ---------------------------
def generate_podcast_script(article_text):
    print("\nGenerating podcast script via Gemini...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
Summarize the following article into a detailed podcast script (~300 words) as a conversation:
- Include a "Host" and an "Expert".
- Each line should start with "Host:" or "Expert:".
- Make it engaging, explanatory, and conversational.

Article:
---
{article_text}
---
"""

    data = {
        "prompt": prompt,
        "temperature": 0.7,
        "candidate_count": 1,
        "max_output_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        script = result['candidates'][0]['content'][0]['text']
        return script
    except Exception as e:
        print(f"⚠️ Failed to generate script from Gemini API: {e}")
        print("Using fallback sample script instead.")
        # Fallback longer script (~1–2 minutes)
        return """
Host: Welcome to our podcast. Today, we discuss a major news story from Haryana.
Expert: IPS officer Y Puran Kumar, 52, left an eight-page final note, naming several retired IAS and IPS officials.
Host: He alleged that he was mentally and administratively tortured during his career.
Expert: His wife, Amneet P Kumar, recently returned from Japan and is demanding justice.
Host: She has refused to allow the post-mortem until her demands are addressed.
Expert: According to sources, she is visibly shattered but determined to see justice done.
Host: This case has raised serious concerns about administrative pressures on officers.
Expert: Absolutely. It's crucial to bring attention to such incidents and ensure accountability.
Host: We'll continue following this story and provide updates in future episodes.
Expert: Stay tuned for more insights and discussions on critical news.
"""


script = generate_podcast_script(article)


# ---------------------------
# 4️⃣ Generate audio for each line using ElevenLabs
# ---------------------------
def generate_audio_elevenlabs(text, voice_id, output_file):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(
            f"Error generating audio: {response.status_code} {response.text}")
        return False


# ---------------------------
# 5️⃣ Generate audio files for each line
# ---------------------------
lines = script.strip().split('\n')
audio_files = []
temp_file_list = "ffmpeg_input_files.txt"

with open(temp_file_list, "w") as f:
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        speaker, text, voice_id = "", "", ""
        if line.lower().startswith("host:"):
            speaker, text, voice_id = "Host", line[5:].strip(), HOST_VOICE_ID
        elif line.lower().startswith("expert:"):
            speaker, text, voice_id = "Expert", line[7:].strip(
            ), EXPERT_VOICE_ID
        else:
            continue

        if not text:
            continue

        output_file = f"temp_audio_{i}.mp3"
        if generate_audio_elevenlabs(text, voice_id, output_file):
            audio_files.append(output_file)
            f.write(f"file '{output_file}'\n")

# ---------------------------
# 6️⃣ Merge audio files using FFmpeg
# ---------------------------
if audio_files:
    output_podcast = "final_podcast.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", temp_file_list,
        "-c", "copy", output_podcast
    ],
                   check=True)
    print(f"\n🎉 Podcast generated successfully: {output_podcast}")
else:
    print("❌ No audio files generated. Podcast creation failed.")

# ---------------------------
# 7️⃣ Cleanup
# ---------------------------
if os.path.exists(temp_file_list):
    os.remove(temp_file_list)
for file in audio_files:
    if os.path.exists(file):
        os.remove(file)
