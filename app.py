from flask import Flask, render_template
from modules.connect_operations import get_notams

app = Flask(__name__)


@app.route("/")
def index():
    # возвращаем шаблон
    return render_template("index.html")


@app.route("/get_notams")
def get_folder_tree():
    # получаем список резервирований

    notams = get_notams()
    return notams


if __name__ == "__main__":
    app.run(debug=True)
