import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load the trained model
with open("models/model.pkl", "rb") as file:
    model = pickle.load(file)

# Load the unique locations
with open("models/locations.pkl", "rb") as file:
    locations = pickle.load(file)

# Load other feature encodings (if any were used during training)
with open("models/column_transformer.pkl", "rb") as file:
    column_transformer = pickle.load(file)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    
    if request.method == "POST":
        location = request.form["location"]
        total_sqft = float(request.form["total_sqft"])
        size = int(request.form["size"])
        bath = int(request.form["bath"])
        balcony = int(request.form["balcony"])
        area_type = request.form["area_type"]
        availability = request.form["availability"]

        # Create a DataFrame for transformation
        input_data = pd.DataFrame(
            [[location, total_sqft, size, bath, balcony, area_type, availability]],
            columns=["location", "total_sqft", "size", "bath", "balcony", "area_type", "availability"]
        )

        # Transform the input data
        input_transformed = column_transformer.transform(input_data)
        
        # Predict the price
        prediction = model.predict(input_transformed)[0]
        prediction = round(prediction, 2)
    
    return render_template("index.html", locations=locations, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
