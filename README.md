# 🤖 Rasa Conversational AI Chatbot

A production-ready **Rasa-based AI chatbot** for **CFSD Digital Services**.  
This chatbot handles **Customer Support, Sales Inquiries, Pricing Information, and Demo Requests** with form validation, MySQL database storage, and multi-channel deployment (Web, Telegram, WhatsApp, Facebook, Instagram).

---

## 🚀 Features

- **Customer Support Module**
  - Collects user details (name, email, phone, product, query, priority)
  - Stores conversations in MySQL

- **Sales Module**
  - Collects sales leads (name, email, phone, designation, company, service, query)
  - Validated form submissions

- **Explore Services**
  - WhatsApp API, SMS, Email, and Chatbot services

- **Pricing Information**
  - WhatsApp, SMS, Email, and Chatbot pricing flows

- **Demo Booking**
  - Request demo form with confirmation messages

- **Database Integration**
  - MySQL storage for forms, intents, and conversation logs
  - Multi-tenant structure for storing data across clients

- **Multi-Channel Support**
  - 🌐 Website (React frontend)
  - 💬 Telegram
  - 📘 Facebook Messenger
  - 📸 Instagram
  - 📱 WhatsApp (via Twilio)

---

## 🛠️ Tech Stack

- **Backend**: [Rasa Open Source](https://rasa.com/)
- **Database**: MySQL
- **Frontend**: React (custom chatbot UI with quick replies & suggestions)
- **Integrations**: Telegram, Facebook, Instagram, WhatsApp
- **Deployment**: Docker
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions (optional)

---

## 📂 Project Structure
.
├── backend/
│ ├── actions/ # Custom actions & validation logic
│ ├── data/ # NLU training data & stories
│ ├── models/ # Trained Rasa models
│ ├── domain.yml # Slots, entities, responses, forms
│ ├── config.yml # NLU + policies configuration
│ ├── credentials.yml # Channel credentials
│ ├── endpoints.yml # Tracker store & action server config
│ └── docker-compose.yml
│
├── frontend/ # React chatbot UI
│ ├── src/components/Chatbot.js
│ └── ...
│
├── docs/ # Documentation & screenshots
│
└── README.md # Project documentation

---

## ⚡ Installation & Setup

### 1️⃣ Clone the Repository

git clone https://github.com/your-username/rasa-chatbot.git
cd rasa-chatbot


###  2️⃣ Setup Backend (Rasa)

cd backend
python -m venv venv
# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

### Train the model:(First-Terminal)
rasa train

### Run action server:(Second-Terminal)
rasa run actions

### Run Rasa server with API enabled:
rasa run --enable-api --cors "*"


### 3️⃣ Setup Frontend (React)
cd frontend
npm install
npm start

Now open 👉 http://localhost:3000



### 🗄️ Database Integration (MySQL)
```
Create a database:
CREATE DATABASE bot_db;

```

### Tables include:

conversation_log → stores full conversations

support_form_data → stores customer support queries

sales_form_data → stores sales leads

channel_credentials → stores multi-channel API tokens

Update endpoints.yml for MySQL tracker store:

tracker_store:
  type: SQL
  dialect: "mysql"
  url: "localhost"
  db: "bot_db"
  username: "root"
  password: "your_password"


### 🧑‍💻 Development Workflow
Train model → rasa train
Run backend (Rasa + Actions)
Run frontend (React chatbot)
Test flows across channels
Store conversations & form data in MySQL


### 📌 Future Enhancements

✅ Add CI/CD with GitHub Actions

✅ Enhance analytics dashboard for conversations

✅ Implement Redis for caching & performance

✅ Multi-language support

### 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss.

### 📜 License

This project is licensed under the MIT License.

### 👨‍💻 Author

Himanshu Yadav
Software Development Engineer @ CFSD - Cloudforce
🔗 LinkedIn
 | GitHub