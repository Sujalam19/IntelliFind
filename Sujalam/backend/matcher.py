from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_db
from mailer import send_match_notification

def check_match(found_desc):
    conn = get_db()
    lost_items = conn.execute("SELECT * FROM lost_items").fetchall()

    for item in lost_items:
        vect = TfidfVectorizer()
        tfidf = vect.fit_transform([item["description"], found_desc])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

        if score > 0.6:
            send_match_notification(item["email"])
            return True

    return False