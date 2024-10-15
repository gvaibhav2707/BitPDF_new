from langchain_community.document_loaders import PyMuPDFLoader
from nltk.tokenize import sent_tokenize
import heapq
import nltk
import os


nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
nltk.data.path.append(nltk_data_path)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))
tokens = word_tokenize("This is a sample sentence")

def summarize_pdf(file_path):
    # Load PDF using PyMuPDFLoader
    loader = PyMuPDFLoader(file_path)
    data = loader.load()

    # Extract the text from the PDF pages
    data = " ".join([page.page_content for page in data])
    text = data.replace("\n", " ")
    text = text.replace("Ɵ", "ti").replace("Ʃ", "tt").replace("Ư", "ff").replace("ﬁ", "fi").replace("ﬂ", "fl")

    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Tokenize words and remove stopwords
    stop_words = set(stopwords.words("english"))
    word_frequencies = {}

    for word in word_tokenize(text):
        if word.lower() not in stop_words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    # Normalize frequencies
    max_freq = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_freq

    # Score sentences based on word frequency
    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_frequencies:
                if len(sent.split(" ")) < 50:  
                    if sent not in sentence_scores:
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    # Extract top N sentences as summary
    summary_sentences = heapq.nlargest(10, sentence_scores, key=sentence_scores.get)
    summary = " ".join(summary_sentences)

    return summary
