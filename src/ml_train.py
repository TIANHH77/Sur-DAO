# src/ml_train.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

usach = pd.DataFrame({
    'nota': [7.0 + i/10 for i in range(100)],
    'riesgo': ['alto' if i % 3 == 0 else 'medio' for i in range(100)],
})

X = usach[['nota']]
y = usach['riesgo']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)
