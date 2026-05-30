from flask import Flask, send_from_directory
from flask_cors import CORS


from API import settings as st

from API.faculties import faculties_bp

from API.Information_Technology.Web.Students.student_registration import student_registration_bp
from API.Information_Technology.Web.Students.student_dashboard import student_dashboard_bp
from API.Information_Technology.Web.Students.student_login import student_login_bp
from API.Information_Technology.Web.Students.student_honorboard import student_honorboard_bp
from API.Information_Technology.Web.Students.student_instructor import student_instructor_bp
from API.Information_Technology.Web.Students.student_sidebar import student_sidebar_bp

from API.Information_Technology.Web.Instructors.instructor_login import instructor_login_bp
from API.Information_Technology.Web.Instructors.instructor_pages import instructor_pages_bp
from API.Information_Technology.Web.Instructors.instructor_notification import instructor_notification_bp
from API.Information_Technology.Web.Instructors.instructor_student import instructor_student_bp
from API.Information_Technology.Web.Instructors.instructor_sidebar import instructor_sidebar_bp
from API.Information_Technology.Web.Instructors.instructor_topbar import instructor_topbar_bp


def create_server():
    app = Flask(
        __name__,
        static_folder=st.WEB_DIR,
        static_url_path=''
    )

    CORS(app)

    app.register_blueprint(faculties_bp)
    app.register_blueprint(student_dashboard_bp)
    app.register_blueprint(student_login_bp)
    app.register_blueprint(student_honorboard_bp)
    app.register_blueprint(student_instructor_bp)
    app.register_blueprint(student_sidebar_bp)
    app.register_blueprint(student_registration_bp)
    app.register_blueprint(instructor_login_bp)
    app.register_blueprint(instructor_pages_bp)
    app.register_blueprint(instructor_notification_bp)
    app.register_blueprint(instructor_student_bp)
    app.register_blueprint(instructor_sidebar_bp)
    app.register_blueprint(instructor_topbar_bp)

    @app.route('/')
    def index():
        return send_from_directory(st.WEB_DIR, 'faculties.html')

    return app

