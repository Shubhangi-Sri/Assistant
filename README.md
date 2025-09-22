
# 🚀 AI-Powered Document & Image Processing Assistant

An end-to-end **full-stack AI assistant** that processes documents & images, performs OCR, leverages **Google Vertex AI (Gemini 1.5)** for intelligent analysis, and provides **query-based responses** via a clean web interface.

This project demonstrates how **AI + OCR + modular backend design** can turn raw documents into a **knowledge assistant** capable of answering questions, summarizing content, and even extending into third-party integrations.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 📌 Features

* 📂 Upload and process **PDF, DOCX, text, and image files**
* 🔍 OCR support via **Google Vision API + Tesseract** for scanned docs/images
* ⚡ Fast ingestion with **caching + multithreading**
* 🤖 AI-powered **question answering & summarization** with **Vertex AI**
* 🌐 Extensible integrations (Wikipedia, Google search, Spotify, weather, etc.)
* 🧩 Modular design – add new endpoints or AI services easily

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🏗️ System Architecture & Workflow

# 🔄 Workflow Breakdown

1. **User Upload**

   * Users upload files (`PDF`, `DOCX`, `TXT`, `Image`) via the web UI
   * Files are validated and stored in the server upload directory

2. **Document Ingestion & Preprocessing**

   * Flask backend detects file type
   * OCR (`Google Vision API + Tesseract`) extracts text from images/scanned PDFs
   * Textual files (`txt`, `docx`, machine-readable PDFs) are read directly

3. **Caching & Threading**

   * Extracted content is cached in memory for speed
   * Multithreaded ingestion ensures smooth, non-blocking processing

4. **AI Model Integration (Vertex AI)**

   * Processed text → **Gemini 1.5 via Vertex AI**
   * Enables summarization, semantic understanding, and contextual Q\&A

5. **Intelligent Querying**

   * API endpoints allow users to **ask questions about their uploaded docs**
   * Backend sends queries + doc context → AI → returns precise answers

6. **Additional Integrations**
7. 
   * Wikipedia & Google search for fact-checking
   * Spotify & weather APIs as optional assistant features

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 📂 Project Structure

| File/Folder             | Purpose                                                                |
| ----------------------- | ---------------------------------------------------------------------- |
| `app.py`                | Core Flask app – handles upload, preprocessing, and AI orchestration   |
| `generate_answers.py`   | Uses AI + doc context to generate accurate answers from uploads        |
| `generate_questions.py` | Utility for generating questions (useful for exams/learning use cases) |
| `requirements.txt`      | Dependency list (Flask, Vertex AI, OCR libraries, Google APIs, etc.)   |
| `uploads/`              | Directory for managing user-uploaded files                             |

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🔀 Data Flow Explained

**Arrows in the diagram represent:**

* 📥 **File flow:** User → Upload → Backend → Preprocessing/OCR → Caching
* ⚙️ **Processing flow:** Cached/processed text → AI Model → Response generation
* ❓ **Query flow:** User Question → API Endpoint → Vertex AI → Response → User

This forms a **robust pipeline** for **knowledge extraction, comprehension, and retrieval** from multiple file types.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🌟 Extensibility & Use Cases

* 🔧 **Extensible Modules:** Easily plug in new endpoints or AI services
* 📚 **Education:** Auto-generate questions/answers from textbooks or notes
* 🏢 **Enterprise Knowledge Management:** Search & query across internal docs
* 📑 **Smart Document Assistant:** Summarize, query, and analyze large reports

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ⚙️ Tech Stack

* **Backend:** Flask, Python
* **AI/ML:** Vertex AI (Gemini-1.5), Google Vision API, Tesseract OCR
* **Integrations:** Wikipedia, Google Search, Spotify API, Weather API
* **Infra:** Multithreading, caching, modular service architecture

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 🚀 Getting Started
## 1️⃣ Clone the repo

```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

# 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Setup environment variables

```
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
export VERTEX_PROJECT_ID="your-gcp-project-id"
```

### 4️⃣ Run the Flask app

```
python app.py
```

### 5️⃣ Open in browser

```
http://127.0.0.1:5000
```

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 🧑‍💻 Example Usage

* Upload a scanned **PDF invoice** → Extract text via OCR → Ask *“What is the invoice total?”*
* Upload a **research paper** → Ask *“Summarize the methodology section”*
* Upload **lecture notes** → Auto-generate **practice questions & answers**

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 📜 License

This project is released under the **MIT License** – free to use, modify, and distribute.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 🤝 Contributions

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to add.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

✨ With this assistant, your documents are no longer static files – they become **interactive, intelligent knowledge sources**.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
