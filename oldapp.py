# from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, Response, json, jsonify
# from werkzeug.utils import secure_filename
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps
# import os, time, datetime, _strptime

# # Local modules (assumed to exist)
# from modules.ocr_extractor import extract_text_from_file
# from modules.database_manager import save_student_data
# from modules.field_extractor import extract_fields
# from modules.summary_generator import generate_summary_report

# # --- App Config ---
# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Replace with a secure key
# UPLOAD_FOLDER = 'database'
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# USER_DB = 'users.json'

# DOCUMENT_FIELDS = {
#     "adhar_card": "Aadhar Card",
#     "pan_card": "PAN Card",
#     "ssc_certificate": "SSC Certificate",
#     "hsc_certificate": "HSC Certificate",
#     "cast_certificate": "Caste Certificate",
#     "cast_validity": "Caste Validity",
#     "non_cremelier": "Non-Creamy Layer Certificate",
#     "domicile": "Domicile Certificate",
#     "school_leaving": "School Leaving Certificate"
# }

# # --- Utility Functions ---
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def load_users():
#     if os.path.exists(USER_DB):
#         with open(USER_DB, 'r') as f:
#             return json.load(f)
#     return {}

# def save_users(users):
#     with open(USER_DB, 'w') as f:
#         json.dump(users, f, indent=2)

# def login_required(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         if 'username' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return wrapper

# def get_available_students():
#     upload_folder = app.config['UPLOAD_FOLDER']
#     if not os.path.exists(upload_folder):
#         return []
#     students = []
#     for folder in os.listdir(upload_folder):
#         if os.path.isdir(os.path.join(upload_folder, folder)):
#             try:
#                 parts = folder.split('_')
#                 if len(parts) == 4:
#                     name, father_name, surname, dob = parts
#                     full_name = f"{name} {father_name} {surname}"
#                     students.append({
#                         'folder': folder,
#                         'display': f"{full_name} — {dob}"
#                     })
#             except ValueError:
#                 continue
#     return students

# # # --- Routes ---
# # @app.route('/index', methods=['GET', 'POST'])
# # @login_required
# # def index():
# #     if request.method == 'POST':
# #         name = request.form.get('name', '').strip()
# #         father_name = request.form.get('father_name', '').strip()
# #         surname = request.form.get('surname', '').strip()
# #         dob = request.form.get('dob', '').strip()

# #         folder_name = f"{name}_{father_name}_{surname}_{dob}"
# #         session['student_folder'] = folder_name
# #         session['student_fullname'] = f"{name} {father_name} {surname}"

# #         save_student_data(name, father_name, surname, dob)
# #         return redirect(url_for('upload_documents'))
# #     return render_template('index.html')


# @app.route('/index', methods=['GET', 'POST'])
# @login_required
# def index():
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         father_name = request.form.get('father_name', '').strip()
#         grandfather_name = request.form.get('grandfather_name', '').strip()
#         surname = request.form.get('surname', '').strip()
#         dob = request.form.get('dob', '').strip()  # Comes as YYYY-MM-DD from date input
#         gender = request.form.get('gender', '').strip()
#         pincode = request.form.get('pincode', '').strip()

#         # Convert DOB to DD/MM/YYYY
#         try:
#             dob_dt = datetime.strptime(dob, "%Y-%m-%d")
#             dob_formatted = dob_dt.strftime("%d/%m/%Y")
#         except ValueError:
#             dob_formatted = "NA"

#         folder_name = f"{name}_{father_name}_{surname}_{dob_formatted.replace('/', '')}"
#         session['student_folder'] = folder_name
#         session['student_fullname'] = f"{name} {father_name} {surname}"

#         save_student_data(name, father_name, grandfather_name, surname, dob_formatted, gender, pincode)
#         return redirect(url_for('upload_documents'))
#     return render_template('index.html')

# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_documents():
#     folder_name = session.get('student_folder')
#     full_name = session.get('student_fullname')
#     if folder_name and not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder_name)):
#         session.pop('student_folder', None)
#         session.pop('student_fullname', None)
#         folder_name = None

#     if request.method == 'POST' and folder_name:
#         folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#         os.makedirs(folder_path, exist_ok=True)
#         for field_key in DOCUMENT_FIELDS:
#             file = request.files.get(field_key)
#             if file and allowed_file(file.filename):
#                 ext = file.filename.rsplit('.', 1)[1].lower()
#                 filename = f"{field_key}.{ext}"
#                 file_path = os.path.join(folder_path, secure_filename(filename))
#                 file.save(file_path)
#         return redirect(url_for('validate_page'))

#     uploaded_files = {}
#     if folder_name:
#         folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#         for key in DOCUMENT_FIELDS:
#             for ext in ALLOWED_EXTENSIONS:
#                 check_path = os.path.join(folder_path, f"{key}.{ext}")
#                 if os.path.exists(check_path):
#                     uploaded_files[key] = f"{key}.{ext}"
#                     break

#     return render_template('upload.html',
#                            full_name=full_name,
#                            folder=folder_name,
#                            doc_fields=DOCUMENT_FIELDS,
#                            uploaded_files=uploaded_files)

# @app.route('/validate-page')
# @login_required
# def validate_page():
#     folder_name = session.get('student_folder')
#     if folder_name and not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder_name)):
#         session.pop('student_folder', None)
#         session.pop('student_fullname', None)
#     return render_template('validate.html')

# @app.route('/view/<folder>/<filename>')
# @login_required
# def view_file(folder, filename):
#     return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

# @app.route('/validate')
# @login_required
# def validate():
#     folder_name = session.get('student_folder')
#     if not folder_name:
#         return "No folder selected", 400

#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

#     def generate():
#         for filename in os.listdir(folder_path):
#             if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
#                 base_name = os.path.splitext(filename)[0]
#                 txt_path = os.path.join(folder_path, f"{base_name}.txt")
#                 if os.path.exists(txt_path):
#                     yield f"data:Skipped (already exists): {base_name}.txt\n\n"
#                     continue
#                 file_path = os.path.join(folder_path, filename)
#                 try:
#                     message = extract_text_from_file(file_path, folder_path)
#                 except Exception as e:
#                     message = f"Error processing {filename}: {str(e)}"
#                 yield f"data:{message}\n\n"
#                 time.sleep(0.5)
#         yield "data:Done\n\n"
#     return Response(generate(), mimetype='text/event-stream')

# # @app.route('/extract-fields')
# # @login_required
# # def extract_fields_route():
# #     folder_name = session.get('student_folder')
# #     if not folder_name:
# #         return "No folder selected", 400

# #     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
# #     all_fields_path = os.path.join(folder_path, "all_fields.json")

# #     if os.path.exists(all_fields_path):
# #         with open(all_fields_path, "r", encoding="utf-8") as f:
# #             all_data = json.load(f)
# #     else:
# #         all_data = {}

# #     def generate():
# #         for filename in os.listdir(folder_path):
# #             if filename.lower().endswith('.txt'):
# #                 doc_name = os.path.splitext(filename)[0]
# #                 if doc_name in all_data:
# #                     yield f"data:📄 {doc_name}: (skipped - already extracted)\n\n"
# #                     continue
# #                 file_path = os.path.join(folder_path, filename)
# #                 result = extract_fields(file_path)
# #                 all_data[doc_name] = result
# #                 with open(all_fields_path, "w", encoding="utf-8") as f:
# #                     json.dump(all_data, f, indent=4, ensure_ascii=False)
# #                 yield f"data:📄 {doc_name}: {json.dumps(result, ensure_ascii=False)}\n\n"
# #                 time.sleep(0.5)
# #         yield "data:Done\n\n"
# #     return Response(generate(), mimetype='text/event-stream')

# # ... (other imports and code remain unchanged)

# @app.route('/extract-fields')
# @login_required
# def extract_fields_route():
#     folder_name = session.get('student_folder')
#     if not folder_name:
#         return "No folder selected", 400

#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#     all_fields_path = os.path.join(folder_path, "all_fields.json")

#     # Load existing data if it exists
#     if os.path.exists(all_fields_path):
#         with open(all_fields_path, "r", encoding="utf-8") as f:
#             all_data = json.load(f)
#     else:
#         all_data = {}

#     def generate():
#         for filename in os.listdir(folder_path):
#             if filename.lower().endswith('.txt'):
#                 doc_name = os.path.splitext(filename)[0]
#                 if doc_name in all_data:
#                     yield f"data:📄 {doc_name}: (skipped - already extracted)\n\n"
#                     continue
                
#                 file_path = os.path.join(folder_path, filename)
#                 try:
#                     result = extract_fields(file_path)
#                     if "error" in result:
#                         yield f"data:📄 {doc_name}: Error - {result['error']}\n\n"
#                     else:
#                         all_data[doc_name] = result
#                         with open(all_fields_path, "w", encoding="utf-8") as f:
#                             json.dump(all_data, f, indent=4, ensure_ascii=False)
#                         yield f"data:📄 {doc_name}: {json.dumps(result, ensure_ascii=False)}\n\n"
#                 except Exception as e:
#                     yield f"data:📄 {doc_name}: Error - {str(e)}\n\n"
                
#                 time.sleep(0.5)
#         yield "data:Done\n\n"
    
#     return Response(generate(), mimetype='text/event-stream')

# # ... (rest of the app.py code remains unchanged)

# @app.route('/check-validation-status')
# @login_required
# def check_validation_status():
#     folder_name = session.get('student_folder')
#     if not folder_name or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder_name)):
#         return jsonify({'status': 'needs_upload'})

#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#     all_fields_path = os.path.join(folder_path, "all_fields.json")
#     has_documents = any(filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')) 
#                        for filename in os.listdir(folder_path))
    
#     if not has_documents:
#         return jsonify({'status': 'needs_upload'})
#     elif not os.path.exists(all_fields_path):
#         return jsonify({'status': 'needs_validation'})
#     else:
#         return jsonify({'status': 'validated'})

# @app.route('/result')
# @login_required
# def result_page():
#     folder_name = session.get('student_folder')
#     if not folder_name or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder_name)):
#         session.pop('student_folder', None)
#         session.pop('student_fullname', None)
#         return render_template("result.html", student=None, extracted_data={}, user_input={}, pending_step=None)

#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#     all_fields_path = os.path.join(folder_path, "all_fields.json")
#     user_input_path = os.path.join(folder_path, "student_data.json")

#     extracted_data = {}
#     user_input = {}
#     pending_step = None

#     if not os.path.exists(user_input_path):
#         pending_step = "upload"
#     elif not os.path.exists(all_fields_path):
#         pending_step = "validate"
#     else:
#         with open(all_fields_path, "r", encoding="utf-8") as f:
#             extracted_data = json.load(f)
#         if os.path.exists(user_input_path):
#             with open(user_input_path, "r", encoding="utf-8") as f:
#                 user_input = json.load(f)

#     return render_template("result.html", 
#                          student=folder_name, 
#                          extracted_data=extracted_data, 
#                          user_input=user_input, 
#                          pending_step=pending_step,
#                          doc_fields=DOCUMENT_FIELDS)

# @app.route('/summary')
# @login_required
# def summary_report():
#     folder_name = session.get('student_folder')
#     if not folder_name or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder_name)):
#         session.pop('student_folder', None)
#         session.pop('student_fullname', None)
#         return redirect(url_for('index'))

#     folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
#     user_input_path = os.path.join(folder_path, "student_data.json")
#     all_fields_path = os.path.join(folder_path, "all_fields.json")

#     if not os.path.exists(user_input_path) or not os.path.exists(all_fields_path):
#         return "Summary cannot be generated. Please complete previous steps."

#     summary = generate_summary_report(user_input_path, all_fields_path)
#     return render_template("summary.html", summary_text=summary, student=folder_name)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']

#         if password != confirm_password:
#             return render_template('signup.html', error="Passwords do not match.")
#         users = load_users()
#         if username in users:
#             return render_template('signup.html', error="User already exists.")
#         users[username] = generate_password_hash(password)
#         save_users(users)
#         return redirect(url_for('login'))
#     return render_template('signup.html')

# @app.route('/')
# def landing():
#     return render_template('landing.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         users = load_users()
#         if username in users and check_password_hash(users[username], password):
#             session['username'] = username
#             return redirect(url_for('index'))
#         return render_template('login.html', error="Invalid username or password.")
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     session.pop('student_folder', None)
#     session.pop('student_fullname', None)
#     return redirect(url_for('login'))

# @app.route('/get-students', methods=['GET'])
# @login_required
# def get_students():
#     students = get_available_students()
#     return jsonify(students)

# @app.route('/select-student', methods=['POST'])
# @login_required
# def select_student():
#     data = request.get_json()
#     student_folder = data.get('student_folder')
#     if student_folder and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], student_folder)):
#         session['student_folder'] = student_folder
#         parts = student_folder.split('_')
#         if len(parts) == 4:
#             name, father_name, surname, _ = parts
#             session['student_fullname'] = f"{name} {father_name} {surname}"
#         return jsonify({'success': True})
#     return jsonify({'success': False}), 400

# if __name__ == '__main__':
#     app.run(debug=True)