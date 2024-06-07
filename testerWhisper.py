import streamlit as st
import azure.cognitiveservices.speech as speechsdk

# Define variables for the subscription key and service region
SUBSCRIPTION_KEY = 'subscription_key'
SERVICE_REGION = 'service_region'

# Text file to store the chunks
file_path = 'script.txt'

# Initialize session state variables if they don't exist
if SUBSCRIPTION_KEY not in st.session_state:
    st.session_state[SUBSCRIPTION_KEY] = ''
if SERVICE_REGION not in st.session_state:
    st.session_state[SERVICE_REGION] = 'westus'

chunks = []
recognizer = None

def recognized_callback(evt):
    global chunks
    global recognizer
    while True:
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            rec_text = evt.result.text
            if "Stop Muse" in rec_text:
                print(f"Recognized End: {rec_text}")
                recognizer.stop_continuous_recognition()
                exit()
            else:
                with open(file_path, 'a') as f:
                    f.write(rec_text + '\n')
                print(f"Recognized: {rec_text}")
                exit()

def page_config():
    st.title("Configuration")
    st.session_state[SUBSCRIPTION_KEY] = st.text_input("Enter your Azure Subscription Key", type='password')
    st.session_state[SERVICE_REGION] = st.text_input("Enter your Azure Service Region", value='westus')
    if st.button("Save and Continue"):
        st.session_state['configured'] = True
        st.experimental_rerun()

def page_recognition():
    global recognizer

    st.title("Azure Speech Service with Streamlit")

    if 'configured' not in st.session_state or not st.session_state['configured']:
        st.warning("Please configure your settings first.")
        return

    subscription_key = st.session_state[SUBSCRIPTION_KEY]
    service_region = st.session_state[SERVICE_REGION]
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    recognizer.recognized.connect(recognized_callback)
    
    if st.button("Start"):
        recognizer.start_continuous_recognition()
        st.write("Speak into your microphone.")
    
    if st.button("End"):
        if recognizer is not None:
            recognizer.stop_continuous_recognition()
            with open(file_path, 'r') as f:
                st.text_area("Recognized Text", f.read(), height=200)
            with open(file_path, 'w') as f:
                f.write("")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Configuration", "Recognition"])

    if page == "Configuration":
        page_config()
    elif page == "Recognition":
        page_recognition()

if __name__ == "__main__":
    main()
