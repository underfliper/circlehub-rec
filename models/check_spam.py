import re
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from joblib import load


def clean_comment(comment):
    comment = re.sub('https?://\S+|www\.\S+', 'link', comment)
    comment = re.sub('[^a-zA-Z]', ' ', comment)
    comment = re.sub('\s+', ' ', comment)
    comment = comment.lower()
    comment = comment.split()

    ps = PorterStemmer()

    comment = [ps.stem(word) for word in comment]
    comment = ' '.join(comment)

    return comment


def check_comment(text):
    loaded_model = load('models\spam_model.joblib')
    loaded_matrix = load('models\spam_matrix.joblib')
    comment = clean_comment(text)

    data = loaded_matrix.transform([comment]).toarray()
    result = loaded_model.predict(data).item(0)

    return {"text": text, "isSpam": True if (result == 1) else False}
    