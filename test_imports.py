import os
from PyPDF2 import PdfReader
from flask import Flask, render_template, jsonify, request, redirect, session, flash
from flask_cors import CORS
import pyttsx3
import datetime
import webbrowser
import pyautogui
import wikipediaapi
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from werkzeug.utils import secure_filename
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import requests
import time

print("All imports are working correctly!")
