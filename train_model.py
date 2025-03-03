import pandas as pd
import numpy as np
import pickle
import re
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Load dataset
df = pd.read_csv("Bengaluru_House_Data.csv")

def convert_sqft_to_float(sqft):
    """
    Convert sqft values to float.
    If there's a range (e.g., '1200 - 1500'), take the average.
    If sqft is already a number, return it as float.
    """
    try:
        if '-' in sqft:
            values = list(map(float, sqft.split('-')))
            return np.mean(values)
        elif re.search(r'\d+', sqft):  # Extract numeric values
            num = re.findall(r'\d+', sqft)
            return float(num[0]) if num else None
        return float(sqft)
    except:
        return None

# Clean 'total_sqft' column
df["total_sqft"] = df["total_sqft"].astype(str).apply(convert_sqft_to_float)
df = df.dropna(subset=["total_sqft"])  # Remove rows where sqft is NaN

# Select features and target variable
features = ["location", "total_sqft", "size", "bath", "balcony", "area_type", "availability"]
target = "price"

df = df[features + [target]]
df = df.dropna()

# Convert 'size' (e.g., '3 BHK') to numeric
df["size"] = df["size"].str.extract(r"(\d+)").astype(float)

# Splitting data into train and test sets
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), ["total_sqft", "size", "bath", "balcony"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["location", "area_type", "availability"])
    ]
)

# Fit and transform the data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

print("X_train shape before transformation:", X_train.shape)
print("X_train shape after transformation:", X_train_transformed.shape)

# Create pipeline
pipeline = Pipeline([
    ("model", LinearRegression())
])

# Train model
pipeline.fit(X_train_transformed, y_train)

# Save the trained model
with open("models/model.pkl", "wb") as file:
    pickle.dump(pipeline, file)

# Save unique locations for dropdown options
with open("models/locations.pkl", "wb") as file:
    pickle.dump(sorted(df["location"].unique()), file)

# Save column transformer for input preprocessing
with open("models/column_transformer.pkl", "wb") as file:
    pickle.dump(preprocessor, file)

print("Model training completed and saved successfully!")
