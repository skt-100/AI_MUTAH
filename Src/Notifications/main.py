from flask import Flask, request, jsonify, render_template
from notifier import notify_section_change

app = Flask(__name__)


# ── صفحة الأدمن ───────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── تطبيق التغيير وإرسال الإشعارات ───────────────────────
@app.route("/notify", methods=["POST"])
def notify():
    data        = request.json
    section_id  = data.get("section_id")
    change_type = data.get("change_type")
    new_value   = data.get("new_value")

    if not all([section_id, change_type, new_value]):
        return jsonify({"status": "error", "message": "البيانات غير مكتملة"}), 400

    result = notify_section_change(int(section_id), change_type, new_value)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
