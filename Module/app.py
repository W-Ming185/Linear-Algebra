"""
Smoothie Recipe Calculator - web interface.

The solver (solver.py) is your friend's script, untouched. This app simply
"types" the answers into it (targets, ingredient numbers, "exit") exactly as
a person would at the console, then reads what it prints and shows it nicely.

Run:   python app.py        then open  http://127.0.0.1:5000
"""
import os
import subprocess
import sys

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, 
                   "smoothie_model_ready.csv")

app = Flask(__name__, static_folder=os.path.join(BASE, "static"))


def load_db():
    df = pd.read_csv(CSV, sep=",")
    items = []
    for i, row in df.iterrows():
        items.append({
            # The solver picks ingredients by line number in the file
            # (line 0 = header), so the first food is number 1.
            "id": int(i) + 1,
            "name": str(row.iloc[1]),
            "protein": float(row.iloc[2]),
            "carb": float(row.iloc[3]),
            "fat": float(row.iloc[4]),
            "fiber": float(row.iloc[5]),
            "kcal": float(row.iloc[6]),
        })
    return items


DB = load_db()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/ingredients")
def ingredients():
    return jsonify(DB)


def parse_output(out):
    lines = [l.rstrip() for l in out.splitlines()]
    res = {"method": None, "items": [], "error": None, "totals": {}}
    section = None
    for l in lines:
        s = l.strip()
        if s.startswith("USing "):
            res["method"] = s.replace("USing", "").strip()
        elif s.startswith("Ingredient_List"):
            section = "list"
        elif s.startswith("Error :"):
            res["error"] = s.split(":", 1)[1].strip()
            section = None
        elif s.startswith("Total :"):
            section = "total"
        elif section == "list" and " : " in s and s.endswith(" g"):
            name, amt = s.rsplit(" : ", 1)
            res["items"].append({"name": name, "grams": float(amt[:-2])})
        elif section == "total" and " : " in s:
            k, v = s.split(" : ", 1)
            k = k.strip().lower()
            num = float(v.split()[0])
            if "protein" in k:
                res["totals"]["protein"] = num
            elif "carb" in k:
                res["totals"]["carb"] = num
            elif "fat" in k:
                res["totals"]["fat"] = num
            elif "fib" in k:
                res["totals"]["fiber"] = num
            elif "energy" in k:
                res["totals"]["kcal"] = num
            elif "price" in k:
                res["totals"]["price"] = num
    return res


@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True)
    try:
        targets = [float(data[k]) for k in ("protein", "carb", "fat", "fiber")]
        ids = []
        for i in data["ids"]:
            i = int(i)
            if i < 1 or i > len(DB):
                raise ValueError(f"Unknown ingredient number {i}")
            if i not in ids:
                ids.append(i)
        if not ids:
            raise ValueError("Pick at least one ingredient.")
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"ok": False, "error": f"Invalid input: {e}"}), 400

    # Exactly what a person would type into the original script
    typed = "\n".join([str(t) for t in targets] + [str(i) for i in ids] + ["exit"]) + "\n"

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run([sys.executable, "solver.py"], input=typed, text=True,
                           capture_output=True, cwd=BASE, env=env, timeout=60)
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Solver timed out."}), 500

    if p.returncode != 0:
        return jsonify({"ok": False, "error": "Solver failed.",
                        "detail": p.stderr[-1500:]}), 500

    result = parse_output(p.stdout)
    result["ok"] = True
    result["raw"] = p.stdout
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False, port=5000)
