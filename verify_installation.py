from transformers import pipeline

# Initialize a simple pipeline to check installation
classifier = pipeline('sentiment-analysis')
result = classifier("I love using Hugging Face's transformers library!")
print(result)
