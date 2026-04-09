import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("creditcard.csv")

X = data.drop("Class", axis=1)
y = data["Class"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 👇 THIS IS WHERE YOU ADD IT
model = RandomForestClassifier(
    class_weight="balanced",
    n_estimators=100,
    max_depth=10
)

model.fit(X_train, y_train)

joblib.dump(model, "model.pkl")

print("Model retrained!")