import json
import random
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from thefuzz import fuzz

app = Flask(__name__)
CORS(app)

INTENTS_FILE = 'intents.json'

def load_intents():
    try:
        with open(INTENTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"intents": []}

def save_intents(data):
    with open(INTENTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

data = load_intents()
user_states = {}

# Context-aware professional cloud intelligence database mapping (Updated with your Q&A)
CLOUD_INTELLIGENCE = {
    "☁️ Cloud Services": [
        "Cloud computing is the delivery of computing resources such as servers, storage, databases, and software over the internet.",
        "Cloud computing offers scalability, cost savings, flexibility, reliability, and remote accessibility.",
        "The main types of cloud computing are Public Cloud, Private Cloud, and Hybrid Cloud.",
        "Software as a Service (SaaS) delivers software applications over the internet without requiring local installation.",
        "Platform as a Service (PaaS) provides a platform for developing, testing, and deploying applications.",
        "Infrastructure as a Service (IaaS) provides virtualized computing resources such as servers and storage."
    ],
    "☁️ AWS": [
        "AWS (Amazon Web Services) is a cloud platform that provides computing, storage, networking, and security services.",
        "Amazon EC2 is a virtual server service that allows users to run applications in the cloud.",
        "Amazon S3 is a cloud storage service used to store and retrieve data securely.",
        "AWS Lambda is a serverless computing service that runs code without managing servers.",
        "Amazon RDS is a managed database service that supports multiple database engines.",
        "CloudWatch is a monitoring service for AWS resources and applications."
    ],
    "☁️ Microsoft Azure": [
        "Microsoft Azure is a cloud platform that provides infrastructure, software, and platform services.",
        "Azure Virtual Machine is a cloud-based virtual server service.",
        "Azure Storage provides secure and scalable cloud storage solutions.",
        "Azure App Service is a platform for building and hosting web applications.",
        "Azure Active Directory is a cloud-based identity and access management service."
    ],
    "☁️ Google Cloud": [
        "Google Cloud Platform (GCP) provides cloud services including computing, storage, networking, and AI solutions.",
        "Google Compute Engine provides virtual machines that run in Google data centers.",
        "Google Cloud Storage is a scalable cloud storage solution for data and applications.",
        "Google Kubernetes Engine (GKE) is a managed Kubernetes service for deploying containerized applications.",
        "BigQuery is Google's serverless data warehouse for analytics and reporting."
    ],
    "🔒 Cloud Security": [
        "Cloud security refers to policies, technologies, and controls used to protect cloud systems and data.",
        "Cloud security protects sensitive information from cyber threats and unauthorized access.",
        "Multi-Factor Authentication (MFA) requires users to verify their identity using multiple authentication methods.",
        "Encryption converts data into a secure format that can only be read with the correct key.",
        "A firewall monitors and controls incoming and outgoing network traffic.",
        "Identity and Access Management (IAM) controls user permissions and access to cloud resources."
    ],
    "🚀 Deployment": [
        "Deployment is the process of making an application available for users.",
        "Cloud deployment involves hosting applications on cloud infrastructure.",
        "CI/CD stands for Continuous Integration and Continuous Deployment, which automate software delivery.",
        "Docker is a platform used to package applications into containers.",
        "Kubernetes is a container orchestration platform used to manage containerized applications.",
        "Flask applications can be deployed on Render, Railway, AWS, Azure, or Google Cloud."
    ],
    "💾 Storage": [
        "Cloud storage allows users to store and access data through the internet.",
        "Cloud storage offers scalability, accessibility, backup, and cost efficiency.",
        "Object storage stores data as objects and is commonly used in cloud environments.",
        "Block storage divides data into blocks and is commonly used for databases and virtual machines.",
        "Backup storage is used to store copies of data for recovery purposes."
    ],
    "🌐 Networking": [
        "Cloud networking connects cloud resources and services through virtual networks.",
        "A Virtual Private Cloud (VPC) is an isolated virtual network within a cloud platform.",
        "A subnet is a segmented portion of a network used for organization and security.",
        "A load balancer distributes incoming traffic across multiple servers.",
        "DNS translates domain names into IP addresses.",
        "A Virtual Private Network (VPN) provides secure communication over public networks."
    ]
}

def get_local_response(user_text):
    user_text = user_text.lower().strip()
    best_match_tag = None
    highest_score = 0
    CONFIDENCE_THRESHOLD = 65
    
    for intent in data['intents']:
        for pattern in intent['patterns']:
            score = fuzz.token_set_ratio(user_text, pattern.lower())
            if score > highest_score:
                highest_score = score
                best_match_tag = intent
                
    if highest_score >= CONFIDENCE_THRESHOLD and best_match_tag:
        return random.choice(best_match_tag['responses'])
    return None

@app.route('/chat', methods=['POST'])
def chat():
    global data
    user_id = request.remote_addr
    
    user_message = request.json.get("message")
    user_context = request.json.get("context", "General")
    
    if not user_message:
        return jsonify({"error": "Missing message content"}), 400
    
    time.sleep(0.5)
    
    if user_id in user_states and user_states[user_id]['state'] == 'waiting_for_answer':
        unanswered_question = user_states[user_id]['question']
        new_answer = user_message.strip()
        
        new_intent = {
            "tag": f"learned_{int(time.time())}",
            "patterns": [unanswered_question],
            "responses": [new_answer]
        }
        
        data['intents'].append(new_intent)
        save_intents(data)
        
        del user_states[user_id]
        return jsonify({"response": "Thank you! I have successfully integrated that cloud solution into my local memory structure."})

    # 1. First check in intents.json using Fuzzy Matching
    bot_reply = get_local_response(user_message)
    if bot_reply:
        return jsonify({"response": bot_reply})
        
    # 2. Advanced Fuzzy Matching inside CLOUD_INTELLIGENCE arrays if no direct intent match
    user_msg_clean = user_message.lower().strip()
    best_cloud_reply = None
    highest_cloud_score = 0
    
    # If a specific context is selected, search there first, otherwise search everywhere
    categories_to_search = [user_context] if user_context in CLOUD_INTELLIGENCE else CLOUD_INTELLIGENCE.keys()
    
    for cat in categories_to_search:
        for info in CLOUD_INTELLIGENCE[cat]:
            score = fuzz.partial_token_set_ratio(user_msg_clean, info.lower())
            if score > highest_cloud_score:
                highest_cloud_score = score
                best_cloud_reply = info

    if highest_cloud_score >= 70 and best_cloud_reply:
        return jsonify({"response": best_cloud_reply})

    # 3. Fallback to learning trigger mode if everything else fails
    user_states[user_id] = {
        'state': 'waiting_for_answer',
        'question': user_message.strip()
    }
    bot_reply = "I lack an exact architecture layout for this problem in my datasets. Could you provide a quick workaround or the expected solution to teach me?"
        
    return jsonify({"response": bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)