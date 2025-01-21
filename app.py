from flask import Flask , render_template , request , session , jsonify , redirect , url_for , flash
from pymongo import MongoClient
import uuid
from werkzeug.security import generate_password_hash , check_password_hash

app = Flask(__name__)
app.secret_key = '12345678'
client = MongoClient('mongodb://localhost:27017/')
db = client['sentimatrix']

default_config_settings = {
    'Use_Local_Sentiment_LLM': True,
    'Use_Local_Emotion_LLM': True,
    'Use_Local_General_LLM': False,
    'Use_Groq_API': False,
    'Use_Gemini_API': False,
    'Use_Open_API': False,
    'Use_Local_Scraper': False,
    'Use_Scraper_API': True,
    'Local_Sentiment_LLM': "cardiffnlp/twitter-roberta-base-sentiment-latest",
    'Local_General_LLM': "llama3.1",
    'Local_Emotion_LLM': "SamLowe/roberta-base-go_emotions",
    'Groq_API': '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',
    'OpenAi_API': None,
    'HuggingFace_API': None,
    'Google_API': None,
    'Local_api_key': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Scraper_api_key': '7ebf4f26faa024ef86d97279c16c2a0c',
    'Groq_LLM': "llama3-8b-8192",
    'OpenAI_LLM': "GPT-3.5",
    'Gemini_LLM': "gemini-1.5-pro",
    'device_map': "auto",
    'Ollama_Model_EndPoint': "http://localhost:11434/api/generate",
    'get_Groq_Review': False,
    'get_Gemini_Review': False,
    'get_OpenAI_review': False,
    'get_localLLM_review': False,
    'Groq_LLM_Temperature': 0.1,
    'Groq_LLM_Max_Tokens': 100,
    'Groq_LLM_Max_Input_Tokens': 300,
    'Groq_LLM_top_p': 1,
    'Groq_LLM_stream': False,
    'OpenAI_LLM_Temperature': 0.1,
    'OpenAI_LLM_Max_Tokens': 100,
    'OpenAI_LLM_stream': False,
    'OpenAI_LLM_Max_Input_Tokens': 300,
    'Local_LLM_Max_Input_Tokens': 300,
    'Gemini_LLM_Temperature': 0.1,
    'Gemini_LLM_Max_Tokens': 100,
    'Gemini_LLM_Max_Input_Tokens': 300,
    'Ollama_Model': "llama3.1",
    'Use_Bar_chart_visualize': False,
    'Use_pie_chart_visualize': False,
    'Use_violin_plot_visualize': False,
    'Use_box_plot_visualize': False,
    'Use_histogram_visualize': False,
    'Use_Card_Emotion_Visulize': False,
    'LLava_Model': "llava",
    'Custom_Prompt': "Explain what's happening in the image and give a detailed response. Also mention what kind of emotion does the image about",
    'IMDB_API': None,
    'platforms': ["playstation-5", "pc", "playstation-4"],
    'reddit_client_id': 'qzUTCldtSi4hU19EXseCFg',
    'reddit_client_secret': 'shDZVPvWAH7lb5Oe2NP9tKIqCSTSkQ',
    'reddit_user_agent': 'textextracter/1.0 by/u/DeepReference5190',
    'Product_Name': None,
    'Reviews_Count': None,
    'Youtube_API': None,
    'target_ecommerce_site': [],
    'target_Games': [],
    'target_Streaming_sites': [],
    'target_online_services': []
}

def initialize_user(user_type, user_details):
    unique_id = str(uuid.uuid4())
    user_collection = db[unique_id]

    hashed_password = generate_password_hash(user_details[2],method='pbkdf2:sha256', salt_length=16)

    if user_type == "organisation":
        personal_details = {
            "type": "organisation",
            "unique_id": unique_id,
            "company_name": user_details[0],
            "company_email": user_details[1],
            "password": hashed_password,
            "contact_number": user_details[3],
            "address": user_details[4],
            "industry": user_details[5],
            "employee_count": user_details[6]
        }
    elif user_type == "individual":
        personal_details = {
            "type": "individual",
            "unique_id":unique_id,
            "name": user_details[0],
            "email": user_details[1],
            "password": hashed_password,
            "phone": user_details[3],
            "location": user_details[4],
            "profession": user_details[5]
        }
    else:
        raise ValueError("Invalid user type!")

    user_collection.insert_one({"_id": "personal_details", **personal_details})
    user_collection.insert_one({"_id": "configuration_settings", **default_config_settings})

    return unique_id

@app.route("/signin", methods=['POST','GET'])
def signin():
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        
        personal_details_doc = collection.find_one({"_id": "personal_details", "email": user_email})
        
        if personal_details_doc:
            if check_password_hash(personal_details_doc["password"], user_password):
                session['unique_id'] = collection_name
                print(collection_name)
                return jsonify({"message": "Sign-in successful", "user": session['unique_id']}), 200

    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/organisation_signup', methods=['GET', 'POST'])
def organisation_signup():
    user_type = 'organisation'

    if request.method == 'POST':
        company_name = request.form['name']
        company_email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        industry = request.form['industry']
        employee_count = request.form['employee_count']
        password = request.form['password']
        user_data = [
            company_name,
             company_email,
             password,
             phone,
             address,
             industry,
             employee_count
        ]
        initialize_user(user_type,user_data)
        flash("Registration successful! Please sign in.", "success")
        return redirect(url_for('render_signin_page'))
    return render_template('organisation_signup.html')

@app.route('/individual_signup', methods=['GET', 'POST'])
def individual_signup():
    user_type = 'individual'

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        password = request.form['password']
        
        phone_number = request.form['phone_number']
        profession = request.form['profession']
        location = request.form['location']

        user_data = [
            name,email,password,phone_number,location,profession
        ]
        initialize_user(user_type,user_data)

        flash("Registration successful! Please sign in.", "success")
        return redirect(url_for('render_signin_page'))
    return render_template('individual_signup.html')

@app.route("/render_signin_page")
def render_signin_page():
    return render_template('signin.html')

@app.route('/render_organisation_signup')
def render_organisation_signup():
    return render_template('organisation_signup.html')

@app.route('/render_individual_signup')
def render_individual_signup():
    return render_template('individual_signup.html')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)