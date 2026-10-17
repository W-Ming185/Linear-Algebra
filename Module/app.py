"""
Smoothie Recipe Calculator - web interface.
Run:   python app.py        then open  http://127.0.0.1:5000
"""
import os
import re
import subprocess
import sys

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "smoothie_model_ready.csv")

app = Flask(__name__, static_folder=os.path.join(BASE, "static"))


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def load_db():
    df = pd.read_csv(CSV, sep=",")
    items = []
    for i, row in df.iterrows():
        items.append({
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
    static_index = os.path.join(app.static_folder, "index.html")
    if os.path.exists(static_index):
        return send_from_directory(app.static_folder, "index.html")
    return send_from_directory(BASE, "index.html")


@app.route("/api/ingredients")
def ingredients():
    return jsonify(DB)


def parse_output(out):
    lines = [l.rstrip() for l in out.splitlines()]
    res = {"method": None, "items": [], "error": None, "totals": {}}
    section = None
    for l in lines:
        s = l.strip()
        # With piped stdin, input() prompts and the method share one stdout line.
        method_match = re.search(r"\busing\s+(\S+)\s*$", s, re.IGNORECASE)
        if method_match:
            res["method"] = method_match.group(1)
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


@app.route("/api/solve", methods=["POST", "OPTIONS"])
def solve():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})
        
    data = request.get_json(force=True)
    try:
        targets = [float(data[k]) for k in ("protein", "carb", "fat", "fiber")]
        raw_items = data.get("items", [])
        
        seen = set()
        valid_items = []
        for it in raw_items:
            ing_id = int(it["id"])
            min_g = int(round(float(it.get("min_g", 0))))
            if ing_id < 1 or ing_id > len(DB):
                raise ValueError(f"Unknown ingredient number {ing_id}")
            if min_g < 0:
                raise ValueError("Minimum amount cannot be negative.")
            if ing_id not in seen:
                seen.add(ing_id)
                valid_items.append((ing_id, min_g))
                
        if not valid_items:
            raise ValueError("Pick at least one ingredient.")
            
        # เรียงลำดับ id จากน้อยไปมากให้ตรงกับที่ solver.py อ่าน CSV
        valid_items.sort(key=lambda x: x[0])
        
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"ok": False, "error": f"Invalid input: {e}"}), 400

    typed_lines = [str(t) for t in targets]
    for ing_id, min_g in valid_items:
        typed_lines.append(str(ing_id))
        typed_lines.append(str(min_g))
    typed_lines.append("exit")
    
    typed = "\n".join(typed_lines) + "\n"

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
    app.run(debug=True, port=5000)
