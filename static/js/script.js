let btn = document.querySelector("#btn");
let content = document.querySelector("#content");
let voice = document.querySelector("#voice");
let loader = document.querySelector("#loader");
let outputBox = document.getElementById("output-box");
let generatedBox = document.getElementById("generated-box");
let controller = new AbortController();
let synthesis = window.speechSynthesis;

function speak(text) {
    let text_speak = new SpeechSynthesisUtterance(text);
    text_speak.rate = 1;
    text_speak.pitch = 1;
    text_speak.volume = 1;
    text_speak.lang = "en-US";
    synthesis.speak(text_speak);
}

let speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = new speechRecognition();
let awaitingSongNameForSpotify = false;
let awaitingSongNameForYouTube = false;

recognition.onstart = () => {
    console.log("Voice recognition started.");
    btn.disabled = true;  // Disable button while recognizing
    loader.style.display = "block";  // Show loader
};

recognition.onend = () => {
    console.log("Voice recognition ended.");
    btn.disabled = false;  // Re-enable button after recognizing
    loader.style.display = "none";  // Hide loader
};

recognition.onresult = (event) => {
    let currentIndex = event.resultIndex;
    let transcript = event.results[currentIndex][0].transcript;
    console.log("Transcription: ", transcript); // Debugging
    content.innerText = transcript;

    if (awaitingSongNameForSpotify) {
        awaitingSongNameForSpotify = false;
        takeCommand(`play ${transcript} spotify`);
    } else if (awaitingSongNameForYouTube) {
        awaitingSongNameForYouTube = false;
        takeCommand(`play ${transcript} video`);
    } else {
        let command = transcript.toLowerCase();
        console.log("Sending command: ", command); // Debugging
        takeCommand(command);
    }
};

btn.addEventListener("click", () => {
    console.log("Starting voice recognition.");
    recognition.start();
});

document.getElementById("stop-button").addEventListener("click", () => {
    controller.abort();
    synthesis.cancel();
    recognition.stop();
    loader.style.display = "none";
    speak("Generation stopped.");
});

function takeCommand(message) {
    console.log("Preparing to send command to server:", message); // Debugging

    controller = new AbortController();

    console.log("Sending command to server:", message); // Debugging
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: message }),
        signal: controller.signal
    })
    .then((response) => response.json())
    .then((data) => {
        console.log("Response from server: ", data); // Debugging
        let responseText = data.response;

        // Create a new response card element
        let responseCard = document.createElement('div');
        responseCard.className = 'response-card';
        responseCard.innerText = responseText;

        // Clear the existing output box and add the new response card
        outputBox.innerHTML = '';
        outputBox.appendChild(responseCard);

        generatedBox.style.display = "block";  // Show the generated box

        if (responseText.includes('Which song video would you like me to play?')) {
            awaitingSongNameForYouTube = true;
        } else if (responseText.includes('Which song would you like me to play on Spotify?')) {
            awaitingSongNameForSpotify = true;
        }
        speak(responseText);
    })
    .catch((error) => {
        if (error.name === 'AbortError') {
            console.log("Fetch aborted.");
        } else {
            console.error("Error:", error);
        }
    });
}

document.getElementById("ask-button").addEventListener("click", () => {
    const userInput = document.getElementById("search-bar").value;
    const responseElement = document.getElementById("response");
    loader.style.display = "block";

    controller = new AbortController();

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ input: userInput }),
        signal: controller.signal
    })
    .then((response) => response.json())
    .then((data) => {
        responseElement.textContent = data.response;

        // Create a new response card element
        let responseCard = document.createElement('div');
        responseCard.className = 'response-card';
        responseCard.innerText = data.response;

        // Clear the existing output box and add the new response card
        outputBox.innerHTML = '';
        outputBox.appendChild(responseCard);

        generatedBox.style.display = "block";  // Show the generated box
        speak(data.response);
        loader.style.display = "none";
    })
    .catch((error) => {
        if (error.name === 'AbortError') {
            console.log("Fetch aborted.");
        } else {
            responseElement.textContent = "Error: Unable to connect.";
            console.error(error);
            loader.style.display = "none";
        }
    });
});

// Handle file upload
document.getElementById("upload-form").addEventListener("submit", function(e) {
    e.preventDefault();
    loader.style.display = "block";
    let formData = new FormData();
    let fileInput = document.getElementById("file-upload");
    let files = fileInput.files;

    for (let i = 0; i < files.length; i++) {
        formData.append("files[]", files[i]);
    }

    fetch('/upload', {
        method: "POST",
        body: formData
    })
    .then((response) => response.json())
    .then((data) => {
        let responseElement = document.getElementById("response");
        responseElement.textContent = data.response;
        if (data.file_paths) {
            responseElement.dataset.filePaths = JSON.stringify(data.file_paths);
        }
        speak(data.response);
        loader.style.display = "none";
    })
    .catch((error) => {
        let responseElement = document.getElementById("response");
        responseElement.textContent = "Error: Unable to upload file.";
        console.error(error);
        loader.style.display = "none";
    });
});
