from flask import Flask, render_template, request, redirect, session, url_for
import os
import json
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = 'Heartfilia67@'  # Replace this with a strong secret in production

# Cloudinary configuration
cloudinary.config(
    cloud_name='deknafekw',
    api_key='853598855258885',
    api_secret='kmkkdpuzthGaexIoRlqCsRoA_s8'
)

# Approved users with passwords
ALLOWED_USERS = {
    "sicilina67@gmail.com": "Heartfilia67@",
    "yukinomegumi17@gmail.com": "Heartfilia67@",
    "rinfeli67@gmail.com": "Heartfilia67@",
    "rinfeli7@gmail.com": "Heartfilia67@"
}

@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('watch_home'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/email', methods=['POST'])
def login_email():
    email = request.form.get('email')
    password = request.form.get('password')

    if email in ALLOWED_USERS and ALLOWED_USERS[email] == password:
        session['email'] = email
        return redirect(url_for('watch_home'))
    else:
        return "Access denied: Invalid email or password.", 403

@app.route('/watch-home')
def watch_home():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('watch_home.html')

@app.route('/watch-videos')
def watch_videos():
    if 'email' not in session:
        return redirect(url_for('login'))

    subject = request.args.get('subject')
    videos = []

    if os.path.exists("videos.json"):
        with open("videos.json", "r") as f:
            all_videos = json.load(f)
            videos = [v["url"] for v in all_videos if v["subject"] == subject]

    return render_template("watch_videos.html", subject=subject, videos=videos)

@app.route('/upload-page')
def upload_page():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'email' not in session:
        return redirect(url_for('login'))

    subject = request.form.get('subject')
    file = request.files.get('video')

    if file and subject:
        os.makedirs("temp_upload", exist_ok=True)
        temp_path = os.path.join("temp_upload", file.filename)
        file.save(temp_path)

        file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)

        try:
            if file_size_mb > 100:
                with open(temp_path, "rb") as f:
                    upload_result = cloudinary.uploader.upload_large(f, resource_type="video")
            else:
                upload_result = cloudinary.uploader.upload(temp_path, resource_type="video")

            video_url = upload_result['secure_url']
            os.remove(temp_path)

            video_entry = {"subject": subject, "url": video_url}
            videos = []

            if os.path.exists("videos.json"):
                with open("videos.json", "r") as f:
                    videos = json.load(f)
            if not isinstance(videos, list):
                videos = []

            videos.append(video_entry)

            with open("videos.json", "w") as f:
                json.dump(videos, f, indent=2)

            return redirect(url_for('watch_home') + "?message=success")
        except Exception as e:
            return redirect(url_for('watch_home') + "?message=fail")

    return "Missing subject or video", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
