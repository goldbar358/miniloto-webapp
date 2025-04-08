from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from collections import Counter
import random

app = Flask(__name__)

def fetch_lotowins_miniloto():
    url = "https://lotowins.com/pastloto/pastlotomini/"
    response = requests.get(url, timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    draws = []
    for row in soup.select("table tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 7:
            nums = [int(cols[i].text) for i in range(2, 7)]
            draws.append(nums)
    return draws[:50]

def generate_predictions(draws_50):
    last_draw = draws_50[0]
    flat_numbers = [n for draw in draws_50 for n in draw]
    freq_counter = Counter(flat_numbers)
    top_15 = [num for num, _ in freq_counter.most_common(15)]

    predictions = []
    tries = 0
    while len(predictions) < 5 and tries < 1000:
        common = random.choice(last_draw)
        if common not in top_15:
            tries += 1
            continue
        group = {common}
        while len(group) < 5:
            group.add(random.choice(top_15))
        sorted_group = sorted(group)
        odd = sum(1 for n in sorted_group if n % 2 == 1)
        total = sum(sorted_group)
        if (odd in [2, 3]) and 70 <= total <= 100:
            if sorted_group not in predictions:
                predictions.append(sorted_group)
        tries += 1

    return sorted(last_draw), sorted(top_15), predictions

@app.route("/")
def index():
    draws = fetch_lotowins_miniloto()
    last_draw, top_15, predictions = generate_predictions(draws)
    return render_template("index.html", last_draw=last_draw, top_15=top_15, predictions=predictions)

if __name__ == "__main__":
    app.run(debug=True)
