import os
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from flask import Flask, render_template, jsonify, request, redirect, session, flash
from flask_cors import CORS
import datetime
import webbrowser
import wikipediaapi
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from werkzeug.utils import secure_filename
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import requests
import time
from Crypto.Cipher import AES  # Ensure this import for PyCryptodome
from PIL import Image
import pytesseract  # Importing pytesseract for OCR
from pdf2image import convert_from_path  # Importing pdf2image for PDF conversion
from google.cloud import vision
import io
import threading

# Set the environment variable for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'your_random_secret_key_12345'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

# Only initialize pyttsx3 if NOT on Render
engine = None
if os.getenv("RENDER") is None:
    import pyttsx3
    engine = pyttsx3.init()
else:
    print("Text-to-speech disabled on Render")
    
# Initialize Vertex AI
vertexai.init(project="gemini-443008", location="us-central1")
model = GenerativeModel("gemini-1.5-flash-002")
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]
# Initialize the Vision API client
vision_client = vision.ImageAnnotatorClient()
uploaded_files = []  # Global variable to store uploaded file paths
document_cache = {}  # Global cache to store document content


def generate_response(prompt, context=""):
    responses = model.generate_content(
        [f"{context}\n{prompt}"],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    return "".join(response.text for response in responses)


def speak(text):
    if engine:
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"TTS disabled: {text}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    text = ""
    if ext == 'pdf':
        text = extract_text_from_pdf(file_path)
        if not text.strip():  # If the PDF doesn't contain readable text
            pages = convert_from_path(file_path)
            for page in pages:
                image_path = f"{file_path}_{pages.index(page)}.png"
                page.save(image_path, 'PNG')
                text += extract_text_from_image(image_path)
    elif ext in {'png', 'jpg', 'jpeg'}:
        text += extract_text_from_image(file_path)
    elif ext in {'txt', 'docx'}:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text += file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin1') as file:
                text += file.read()
    return text


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def extract_text_from_image(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_files
    if 'files[]' not in request.files:
        flash('No file part')
        return redirect('/')
    files = request.files.getlist('files[]')
    uploaded_files = []  # Reset the list for each upload
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Check if file already exists
            if os.path.exists(file_path):
                uploaded_files.append(file_path)
                print(f"File {filename} already exists. Using the existing file.")
            else:
                file.save(file_path)
                uploaded_files.append(file_path)
                print(f"File {filename} saved.")
    # Read and cache file content
    threads = []
    for file_path in uploaded_files:
        # Start a new thread to read the file
        thread = threading.Thread(target=cache_file_content, args=(file_path,))
        thread.start()
        threads.append(thread)
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    return jsonify({'response': 'Files successfully uploaded or accessed from cache', 'file_paths': uploaded_files})


def cache_file_content(file_path):
    content = read_file(file_path)
    document_cache[file_path] = content


@app.route('/ask', methods=['POST'])
def ask():
    global uploaded_files
    user_input = request.json.get('input')
    print(f"Received command: {user_input}")  # Debugging
    response = ''
    if 'hello' in user_input or 'hey' in user_input:
        response = "Hello! How can I assist you?"
    elif 'who are you' in user_input:
        response = "I am NEO, your virtual assistant."
    elif 'open youtube' in user_input:
        webbrowser.open("https://youtube.com ")
        response = "Opening YouTube..."
    elif 'time' in user_input:
        current_time = datetime.datetime.now().strftime("%H:%M")
        response = f"The time is {current_time}."
    elif 'date' in user_input:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        response = f"Today's date is {current_date}."
    elif 'play a song on spotify' in user_input:
        response = "Which song would you like me to play on Spotify?"
    elif 'play' in user_input and 'spotify' in user_input:
        query = user_input.replace('play', '').replace('spotify', '').strip()
        response = play_spotify_song(query)
    elif 'play a song video' in user_input:
        response = "Which song video would you like me to play?"
    elif 'play' in user_input and 'video' in user_input:
        query = user_input.replace('play', '').replace('video', '').strip()
        response = play_video(query)

    elif 'search google' in user_input:
        query = user_input.replace('search google', '').strip()
        response = search_google(query)
    elif 'search wikipedia' in user_input:
        query = user_input.replace('search wikipedia', '').strip()
        response = search_wikipedia(query)
    elif 'current weather of' in user_input:
        location = user_input.replace('current weather of', '').strip()
        response = get_weather(location)
    else:
        context = ""
        for file_path in uploaded_files:
            context += document_cache.get(file_path, '')
        response = generate_response(user_input, context)
    print(f"Generated response: {response}")  # Debugging
    return jsonify({'response': response})


from dotenv import load_dotenv
load_dotenv()


def get_weather(location):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    api = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    json_data = requests.get(api).json()
    condition = json_data['weather'][0]['main']
    temp = int(json_data['main']['temp'])
    min_temp = int(json_data['main']['temp_min'])
    max_temp = int(json_data['main']['temp_max'])
    pressure = json_data['main']['pressure']
    humidity = json_data['main']['humidity']
    wind = json_data['wind']['speed']
    sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise']))
    sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset']))
    final_info = f"{condition}\n{temp}°C"
    final_data = (
        f"\nMin Temp: {min_temp}°C\n"
        f"Max Temp: {max_temp}°C\n"
        f"Pressure: {pressure} hPa\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind} m/s\n"
        f"Sunrise: {sunrise}\n"
        f"Sunset: {sunset}"
    )
    return f"The current temperature in {location} is {temp}°C with {condition}. {final_data}"


def play_video(query):
    youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
    request = youtube.search().list(
        part='snippet',
        type='video',
        q=query,
        maxResults=1,
        safeSearch='strict'
    )
    response = request.execute()
    video_url = f" https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
    webbrowser.open(video_url)
    return f"Playing {query} video from YouTube."


def play_spotify_song(query):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri='http://localhost:8888/callback',
            scope='user-library-read user-read-playback-state user-modify-playback-state',
            show_dialog=True
        ))
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_id = track['id']
            devices = sp.devices()
            if devices['devices']:
                device_id = devices['devices'][0]['id']
                sp.start_playback(device_id=device_id, uris=[f'spotify:track:{track_id}'])
                return f"Playing {query} on Spotify."
            else:
                return "No active Spotify device found. Please open Spotify and try again."
        else:
            return "Sorry, I couldn't find that song on Spotify."
    except spotipy.exceptions.SpotifyException as e:
        return f"Spotify error: {e}"


def search_google(query):
    search_url = f" https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    return f"Searching Google for {query}."


def search_wikipedia(query):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='YourAppName/1.0 (your_email@example.com)'
    )
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary[0:1000]
    else:
        return "Sorry, I couldn't find anything on Wikipedia for that query."


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)