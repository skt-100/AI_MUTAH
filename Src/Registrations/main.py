from flask import Flask, request, jsonify, render_template
import registration as reg

app = Flask(__name__)


# ── صفحة الرئيسية ─────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── تقديم طلب تسجيل (الطالب) ─────────────────────────────
@app.route("/request", methods=["POST"])
def submit_request():
    data           = request.json
    student_id     = data.get("student_id")
    course_id      = data.get("course_id")
    section_number = data.get("section_number")

    if not all([student_id, course_id, section_number]):
        return jsonify({"status": "error", "message": "البيانات غير مكتملة"}), 400

    result = reg.submit_request(
        int(student_id),
        int(course_id),
        int(section_number)
    )
    return jsonify(result)


# ── معالجة التسجيل (الأدمن) ──────────────────────────────
@app.route("/process", methods=["POST"])
def process():
    data       = request.json
    section_id = data.get("section_id")

    if not section_id:
        return jsonify({"status": "error", "message": "البيانات غير مكتملة"}), 400

    result = reg.process_all(int(section_id))
    return jsonify(result)


# ── عرض الطلبات مرتبة بالأولوية ──────────────────────────
@app.route("/requests", methods=["GET"])
def get_requests():
    section_id = request.args.get("section_id")

    if not section_id:
        return jsonify({"status": "error", "message": "البيانات غير مكتملة"}), 400

    result = reg.get_requests(int(section_id))
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
