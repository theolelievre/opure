import csv, os, requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
csv_data, last_update = [], None
CSV_URL = 'https://storage.googleapis.com/mollusques-caen/data.csv'

def fetch_csv_data(source):
    global csv_data, last_update
    try:
        if source.startswith("http"):
            headers = {"Range": "bytes=-5040"}
            response = requests.get(source, headers=headers)
            response.raise_for_status()
            lines = response.text.splitlines()
        else:
            with open(source, 'r', encoding='utf-8') as file:
                lines = file.readlines()

        reader = csv.reader(lines)
        csv_data = [row for row in reader if len(row) == 2]
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Erreur CSV : {e}")

def get_current_note():
    try:
        return round((float(csv_data[-1][1]) / 10) * 5) if csv_data else None
    except Exception as e:
        print(f"Erreur note : {e}"); return None

def calculate_weekly_average():
    try:
        now, week_ago = datetime.now(), datetime.now() - timedelta(days=7)
        values = [float(row[1]) for row in csv_data if datetime.strptime(row[0].split("T")[0], "%Y-%m-%d") >= week_ago]
        return round((sum(values) / len(values) / 10) * 5) if values else 0
    except Exception as e:
        print(f"Erreur moyenne : {e}"); return 0

@app.route('/api/note', methods=['GET'])
def note_endpoint():
    global last_update
    format_type = request.args.get('format', 'json').lower()
    if not csv_data: fetch_csv_data(CSV_URL)
    current_note, weekly_avg = get_current_note(), calculate_weekly_average()

    if current_note is None:
        return "Erreur traitement", 500

    if format_type == 'json':
        return jsonify({"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "current_note": current_note, "weekly_avg": weekly_avg, "last_update": last_update})

    if format_type == 'txt':
        return render_template_string("<pre><b>Note : {{ note }}/5\nMoyenne : {{ avg }}/5<b></pre>", note=current_note, avg=weekly_avg)

    return "Format non supportÃ©", 400

def scheduled_task():
    fetch_csv_data(CSV_URL)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', minutes=60)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


#if __name__ == '__main__':
#    app.run(debug=True)