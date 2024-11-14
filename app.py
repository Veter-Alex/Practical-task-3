from flask import Flask, render_template, request
from modules.connect_operations import get_notams

app = Flask(__name__)


@app.route("/")
def index():
    # возвращаем шаблон
    return render_template("index.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/get_notams", methods=["POST"])
def route_get_notams():
    data = request.get_json()
    icao_codes = data["icaoCodes"]
    return get_notams(icao_codes)


if __name__ == "__main__":
    app.run(debug=True)
