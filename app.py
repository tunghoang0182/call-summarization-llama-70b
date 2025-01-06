import streamlit as st
from openai import OpenAI
from groq import Groq
import json
import os

# API keys
openai_api_key = 
groq_api_key = 

# Clients
openai_client = OpenAI(api_key=openai_api_key)
groq_client = Groq(api_key=groq_api_key)

if not os.path.exists('uploads'):
    os.makedirs('uploads')

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
    return response

def summarize_text(text):
    summary_prompt = (
        f"You are a sales assistant tasked with summarizing a phone conversation between a customer and our sales representative at Sunwire Inc. "
        f"Your role is to capture key information from the conversation to help our sales team review it later. "
        f"Be precise when documenting personal information such as addresses, names, emails, etc., and carefully check the spelling of all details. "
        f"In this conversation, the sales representative is the one representing Sunwire Inc., and the other person is the customer. Ensure that the sales representative is correctly identified.\n"
        f"Do not include any details specific to Sunwire Inc., such as Sunwire email addresses (e.g., any ending with sunwire.ca) or internal Sunwire information, under the client's information. Such details should only be mentioned under the Phone Call Key Points or elsewhere as relevant.\n"     
        f"After transcribing the audio, if the content is not a conversation or contains irrelevant information (such as hold music), respond with 'The audio content does not contain a valid conversation for summarization.' Otherwise, summarize the content as instructed."
        f"The summary should follow the format below:\n\n"
        f"Client Information:\n"
        f"Phone Call Key Points: {text}\n"
        f"Customer Notes: Identify the customer based on their inquiries and responses if there is.\n"
        f"Recommendation: Finally, Give some recommendations for our sale team.\n"
    )

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": summary_prompt
            }
        ],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🦙 Call Summarization with llama")

# File uploader for audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "flac", "webm"], label_visibility="collapsed")

if uploaded_file is not None:
    # Save the uploaded file to disk
    file_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)  # Ensure the uploads directory exists
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner('Summarizing transcription...'):
        transcription_response = transcribe_audio(file_path)
        transcription_text = transcription_response.text  # Adjust based on your actual API response structure

        transcription_text_file = file_path.replace(os.path.splitext(file_path)[1], ".txt")
        with open(transcription_text_file, "w") as text_file:
            text_file.write(transcription_text)

        summary_text = summarize_text(transcription_text)

    st.markdown(summary_text)

    with open(transcription_text_file, "r") as text_file:
        st.download_button(
            label="Download Transcription",
            data=text_file.read(),
            file_name=os.path.basename(transcription_text_file),
            mime="text/plain"
        )
