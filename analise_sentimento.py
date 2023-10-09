from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Dados fictícios para treinamento (você precisará de um conjunto de dados real)
data = [
    ("O produto é ótimo!", "positiva", "elogio", "bom"),
    ("Não gostei do produto.", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    ("", "positiva", "elogio", "bom"),
    ("", "negativa", "reclamação", "mau"),
    
    # ... adicione mais exemplos aqui
]
texts, sentiment, feedback, quality = zip(*data)

# Dividir os dados em treinamento e teste
texts_train, texts_test, sentiment_train, sentiment_test, feedback_train, feedback_test, quality_train, quality_test = train_test_split(texts, sentiment, feedback, quality, test_size=0.2)

# Criar modelo para classificação de sentimento
model_sentiment = make_pipeline(TfidfVectorizer(), MultinomialNB()).fit(texts_train, sentiment_train)

# Criar modelo para classificação de feedback
model_feedback = make_pipeline(TfidfVectorizer(), MultinomialNB()).fit(texts_train, feedback_train)

# Criar modelo para classificação de qualidade
model_quality = make_pipeline(TfidfVectorizer(), MultinomialNB()).fit(texts_train, quality_train)

# Avaliar os modelos
print("Sentimento:", classification_report(sentiment_test, model_sentiment.predict(texts_test)))
print("Feedback:", classification_report(feedback_test, model_feedback.predict(texts_test)))
print("Qualidade:", classification_report(quality_test, model_quality.predict(texts_test)))

# Função para classificar uma nova pergunta
def classify_question(question):
    return {
        "Sentimento": model_sentiment.predict([question])[0],
        "Feedback": model_feedback.predict([question])[0],
        "Qualidade": model_quality.predict([question])[0]
    }

# Testar a função
print(classify_question("legal.muito obrigado, adorei a peça."))
