import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ML_DIR = Path(__file__).resolve().parent
DATA_PATH = ML_DIR / "data" / "UpdatedResumeDataSet.csv"
MODEL_PATH = ML_DIR / "models" / "category_classifier.joblib"


def clean(text: str) -> str:
    text = re.sub(r"http\S+|\S+@\S+", " ", str(text))
    text = re.sub(r"[^A-Za-z0-9+#. ]", " ", text)
    return re.sub(r"\s+", " ", text).lower().strip()


# 1. Load the data
df = pd.read_csv(DATA_PATH)
df = df.drop_duplicates(subset="Resume")  # the dataset has many duplicate resumes
df["clean"] = df["Resume"].apply(clean)
print(f"Resumes after removing duplicates: {len(df)}")
print(df["Category"].value_counts())

# 2. Split: 80% to learn from, 20% to test on
X_train, X_test, y_train, y_test = train_test_split(
    df["clean"], df["Category"],
    test_size=0.2, random_state=42, stratify=df["Category"],
)

# 3. Build and train the model
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                              max_features=20000, sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)

# 4. Test it on resumes it has never seen
print("\n--- Results on the test set ---")
print(classification_report(y_test, model.predict(X_test)))

# 5. Save it
MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")