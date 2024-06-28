import os

from upload import upload
from process import process
from base_utils import base_utils

from flask import Flask , request , jsonify , render_template

os.environ['OPENAI_API_KEY'] = 'sk-proj-dy2n6pSZfdYkvy0frXykT3BlbkFJjn2JqvQGvgXhWwr2Hr0Y'

app = Flask(__name__)
open('chat_logs.json' , 'w').write('')

@app.route('/')
def index() : return render_template('temp_3.html')

@app.route('/upload')
def upload_page() : return render_template('admin.html')

@app.route('/api/feedback', methods = ['POST'])
def feedback() : 

    data = request.json

    base_utils.write_to_log(data)

    return jsonify({'status' : 'Feedback received'})

@app.route('/api/chatbot', methods = ['POST'])
def chatbot() : 

    data = request.get_json()

    bot_response = base_utils.get_response_from_llm(data)

    return jsonify(response=bot_response)

@app.route('/api/upload', methods=['POST'])
def upload_file() : 

    file = request.files

    if 'file' not in file : return jsonify({'error' : 'No file part in the request'}) , 400

    file = file['file']

    response = upload.upload(file)

    return response

@app.route('/api/process' , methods = ['POST'])
def process_file() : 

    response = process.process()

    return jsonify({'message' : 'Processing completed successfully.'}) , 200

if __name__ == '__main__' : app.run(debug = True)
