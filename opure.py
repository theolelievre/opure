import requests
import pandas as pd
from flask import Flask, render_template_string

url = "https://storage.googleapis.com/mollusques-caen/data.csv"

def fetch_last_bytes(url, byte_count):
    return requests.get(url, headers={"Range": f"bytes=-{byte_count}"}, timeout=10).content

last_lines = fetch_last_bytes(url, 5040).decode("utf-8").splitlines()
if len(last_lines) < 168: raise Exception("Données insuffisantes.")
data_last_168 = pd.DataFrame([line.split(",") for line in last_lines[-168:]], columns=['timestamp', 'valeurs'])
data_last_168['valeurs'] = pd.to_numeric(data_last_168['valeurs'], errors='coerce')
if data_last_168['valeurs'].isnull().any(): raise Exception("Valeurs non valides.")

mean_last_168 = round(data_last_168['valeurs'].mean() / 2)
last_value_reported = round(data_last_168['valeurs'].iloc[-1] / 2)

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang=\"fr\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Données CSV</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>Données CSV</h1>
    <h2>Moyenne des 168 dernières valeurs : {{ mean_last_168 }}/5</h2>
    <h2>Dernière valeur : {{ last_value_reported }}/5</h2>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(TEMPLATE, mean_last_168=mean_last_168, last_value_reported=last_value_reported)

if __name__ == "__main__":
    app.run(debug=True)