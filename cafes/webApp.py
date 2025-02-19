from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
API = "http://127.0.0.1:5000"

@app.route('/')
def index():
    try:
        resp = requests.get(f"{API}/cafes")
        if resp.status_code == 200:
            cafes = resp.json()
        else:
            cafes = []
    except Exception as e:
        print("Viga API kõnes:", e)
        cafes = []
    return render_template('index.html', cafes=cafes)


@app.route('/filter_open', methods=['POST'])
def filter_open():
    """
    Filtreerimine avamisaja järgi.
    """
    open_time = request.form.get("open_time")
    if not open_time:
        return redirect(url_for('index'))
    resp = requests.get(f"{API}/cafes")
    if resp.status_code == 200:
        all_cafes = resp.json()

        filtered = [c for c in all_cafes if c["time_open"] == open_time]
    else:
        filtered = []

    return render_template('index.html', cafes=filtered)


@app.route('/filter_close', methods=['POST'])
def filter_close():
    """
    Filtreerimine sulgemisaja järgi.
    """
    close_time = request.form.get("close_time")
    if not close_time:
        return redirect(url_for('index'))
    resp = requests.get(f"{API}/cafes")
    if resp.status_code == 200:
        all_cafes = resp.json()
        filtered = [c for c in all_cafes if c["time_closed"] == close_time]
    else:
        filtered = []

    return render_template('index.html', cafes=filtered)


@app.route('/filter_range', methods=['POST'])
def filter_range():
    """
    Filtreerimine lahtioleku vahemiku järgi.
    """
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    params = {"start": start_time, "end": end_time}

    resp = requests.get(f"{API}/cafes/time", params=params)
    if resp.status_code == 200:
        filtered = resp.json()
    else:
        filtered = []

    return render_template('index.html', cafes=filtered)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        name = request.form.get("name")
        location = request.form.get("location")
        service_provider = request.form.get("service_provider")
        time_open = request.form.get("time_open")
        time_closed = request.form.get("time_closed")

        data = {
            "name": name,
            "location": location,
            "service_provider": service_provider,
            "time_open": time_open,
            "time_closed": time_closed
        }
        resp = requests.post(f"{API}/cafes", json=data)
        if resp.status_code == 201:
            return redirect(url_for('index'))
        else:
            return f"Viga lisamisel: {resp.text}", resp.status_code
    else:
        return render_template('add.html')


@app.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
def edit_cafe(cafe_id):
    if request.method == 'GET':
        resp = requests.get(f"{API}/cafes")
        if resp.status_code == 200:
            all_cafes = resp.json()
            cafe_data = next((c for c in all_cafes if c["id"] == cafe_id), None)
            if cafe_data:
                return render_template('edit.html', cafe=cafe_data)
            else:
                return "Kohvikut ei leitud", 404
        else:
            return "Viga API-ga suhtlemisel", resp.status_code

    if request.method == 'POST':
        name = request.form.get("name")
        location = request.form.get("location")
        service_provider = request.form.get("service_provider")
        time_open = request.form.get("time_open")
        time_closed = request.form.get("time_closed")

        data = {
            "name": name,
            "location": location,
            "service_provider": service_provider,
            "time_open": time_open,
            "time_closed": time_closed
        }
        resp = requests.put(f"{API}/cafes/{cafe_id}", json=data)
        if resp.status_code == 200:
            return redirect(url_for('index'))
        else:
            return f"Viga muutmisel: {resp.text}", resp.status_code


@app.route('/delete/<int:cafe_id>')
def delete_cafe(cafe_id):
    resp = requests.delete(f"{API}/cafes/{cafe_id}")
    if resp.status_code == 200:
        return redirect(url_for('index'))
    else:
        return f"Viga kustutamisel: {resp.text}", resp.status_code


if __name__ == "__main__":
    app.run(port=5001)
