from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet,AllSlotsReset, ActiveLoop, ConversationPaused, ConversationResumed
from rasa_sdk.events import UserUtteranceReverted
import mysql.connector
import re
import requests


#database(QUERY,VALUE)
def insert_into_db(query, values):
    try:
        connection = mysql.connector.connect(
            host="localhost",         # Hostname
            user="root",              # MySQL User
            password="2378",       # MySQL Password
            database="rasa_chatbot"   # Database Name
        )
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")


#[Fetch AutoSuggestion]
class ActionGetSuggestion(Action):
    def name(self) -> str:
        return "action_get_suggestion"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict) -> list:
        user_text = tracker.latest_message.get('text')
        response = requests.post("http://localhost:5001/suggest", json={"input": user_text})
        suggestions = response.json().get("suggestions", [])
        
        dispatcher.utter_message(text=f"Suggestions: {', '.join(suggestions)}")
        return []
    

#channel_set_class
class ActionSetUserChannel(Action):
    def name(self) -> str:
        return "action_set_user_channel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        channel = tracker.get_latest_input_channel()
        print(f"User is interacting via: {channel}")

        if channel in ["facebook", "telegram", "instagram"]:
            return [SlotSet("user_channel", channel)]
        else:
            return [SlotSet("user_channel", "web")]


class ActionMainMenu(Action):
    def name(self) -> str:
        return "action_main_menu"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()
        print(f"📢 Detected channel: {channel}")   

        if channel in ["instagram", "facebook"]:  
            message = (
                "👋 Welcome to CFSD!\n"
                "Please type one of these options:\n\n"
                "👉 Explore Services\n"
                "👉 View Pricing\n"
                "👉 Request Demo\n"
                "👉 Customer Support"
            )
            dispatcher.utter_message(text=message)

        elif channel == "rest":
            # Web (REST channel) → Carousel
            cards = [
                {
                    "title": "Explore Services",
                    "subtitle": "Discover our WhatsApp, SMS, Email, and Chatbot solutions.",
                    "image_url": "http://localhost:3000/images/explore_service.png",
                    "buttons": [
                        {"title": "Open", "type": "postback", "payload": "Explore Services"}
                    ]
                },
                {
                    "title": "View Pricing",
                    "subtitle": "Check out our affordable plans for all services.",
                    "image_url": "http://localhost:3000/images/pricing_service.png",
                    "buttons": [
                        {"title": "Open", "type": "postback", "payload": "View Pricing"}
                    ]
                },
                {
                    "title": "Request Demo",
                    "subtitle": "Book a free live demo with our experts.",
                    "image_url": "http://localhost:3000/images/request.png",
                    "buttons": [
                        {"title": "Book Now", "type": "postback", "payload": "Request Demo"}
                    ]
                },
                {
                    "title": "Customer Support",
                    "subtitle": "Get help from our support team.",
                    "image_url": "http://localhost:3000/images/customer_sales.png",
                    "buttons": [
                        {"title": "Contact", "type": "postback", "payload": "Customer Support"}
                    ]
                }
            ]

            dispatcher.utter_message(
                text="👋 Welcome to CFSD! Please choose an option:",
                json_message={"carousel": cards}
            )

        else:
            # Telegram → Buttons
            dispatcher.utter_message(
                text="👋 Welcome to CFSD!\nPlease choose an option:",
                buttons=[
                    {"title": "Explore Services", "payload": "Explore Services"},
                    {"title": "View Pricing", "payload": "View Pricing"},
                    {"title": "Request Demo", "payload": "Request Demo"},
                    {"title": "Customer Support", "payload": "Customer Support"}
                ]
            )

        return []
    
class ActionExploreServices(Action):
    def name(self) -> str:
        return "action_explore_services"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[str, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        # Common message text
        message_text = (
            "Here are the services we offer:\n"
            "✅ WhatsApp Marketing\n"
            "✅ SMS Campaigns\n"
            "✅ Email Automation\n"
            "✅ AI Chatbot Solutions"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        elif channel == "rest":
            # Web / REST → Carousel
            cards = [
                {
                    "title": "WhatsApp API",
                    "subtitle": "Bulk messaging, templates & webhooks",
                    "image_url": "http://localhost:3000/images/whatsapp_1.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "Bulk SMS",
                    "subtitle": "Fast & reliable SMS delivery",
                    "image_url": "http://localhost:3000/images/bulk_sms.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "Email Automation",
                    "subtitle": "Targeted campaigns with analytics & drip workflows",
                    "image_url": "http://localhost:3000/images/bulk_email.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "AI Chatbot",
                    "subtitle": "24x7 customer support & lead-gen",
                    "image_url": "http://localhost:3000/images/chatbot.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                }
            ]
            dispatcher.utter_message(text="Here are some options for you:", json_message={"carousel": cards})

        else:
            # Telegram → Buttons
            dispatcher.utter_message(
                text=message_text,
                buttons=[
                    {"title": "WhatsApp", "payload": "/service_whatsapp"},
                    {"title": "SMS", "payload": "/service_sms"},
                    {"title": "Email", "payload": "/service_email"},
                    {"title": "Chatbot", "payload": "/service_chatbot"}
                ]
            )

        return []

#pricing_main_menu
class ActionPricingInfo(Action):
    def name(self) -> str:
        return "action_pricing_info"

    def run(
        self, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker,
        domain: Dict[str, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        # Common text for Instagram & Facebook
        message_text = (
            "Here are our pricing categories:\n"
            "💰 WhatsApp Pricing\n"
            "💰 SMS Pricing\n"
            "💰 Email Pricing\n"
            "💰 Chatbot Pricing"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        elif channel == "rest":
            # Web / REST → Carousel
            cards = [
                {
                    "title": "WhatsApp Pricing",
                    "subtitle": "₹0.55/template msg | ₹0.35/session msg",
                    "image_url": "http://localhost:3000/images/whatsapp_1.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "SMS Pricing",
                    "subtitle": "₹0.20/promotional | ₹0.25/transactional",
                    "image_url": "http://localhost:3000/images/bulk_sms.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "Email Pricing",
                    "subtitle": "₹0.10/email | ₹1499/month (50k emails)",
                    "image_url": "http://localhost:3000/images/bulk_email.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                },
                {
                    "title": "Chatbot Pricing",
                    "subtitle": "₹1999/month Standard | ₹4999/month Pro",
                    "image_url": "http://localhost:3000/images/chatbot.png",
                    "buttons": [
                        {"title": "📅 Book Demo", "type": "postback", "payload": "/request_demo"},
                        {"title": "📩 Customer Service", "type": "postback", "payload": "/customer_support"}
                    ]
                }
            ]
            dispatcher.utter_message(text="Here are our pricing categories:", json_message={"carousel": cards})

        else:
            # Telegram → Buttons
            dispatcher.utter_message(
                text="Here are our pricing categories. Select a service to view its pricing:",
                buttons=[
                    {"title": "WhatsApp", "payload": "/pricing_whatsapp"},
                    {"title": "SMS", "payload": "/pricing_sms"},
                    {"title": "Email", "payload": "/pricing_email"},
                    {"title": "Chatbot", "payload": "/pricing_chatbot"}
                ]
            )

        return []


#services_class
class ActionServiceWhatsApp(Action):
    def name(self) -> Text:
        return "action_service_whatsapp"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "📱 WhatsApp Marketing:\n"
            "Send personalized messages, bulk campaigns, "
            "and automate responses to your customers via WhatsApp."
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []


class ActionServiceSMS(Action):
    def name(self) -> Text:
        return "action_service_sms"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "📲 SMS Campaigns:\n"
            "Instantly reach users with promotional, transactional, or OTP messages."
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return [] 


class ActionServiceEmail(Action):
    def name(self) -> Text:
        return "action_service_email"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "📧 Email Automation:\n"
            "Run targeted email campaigns with analytics and drip workflows."
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []
    

class ActionServiceChatbot(Action):
    def name(self) -> Text:
        return "action_service_chatbot"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "🤖 AI Chatbot:\n"
            "Provide instant 24x7 customer support or lead generation using our powerful chatbot platform."
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []


#pricing_class
class ActionPricingWhatsApp(Action):
    def name(self) -> Text:
        return "action_pricing_whatsapp"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "💰 WhatsApp Pricing:\n"
            "- ₹0.55/message (template)\n"
            "- ₹0.35/message (session)\n"
            "- ₹999/month platform fee"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []
    
class ActionPricingSMS(Action):
    def name(self) -> Text:
        return "action_pricing_sms"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "💰 SMS Pricing:\n"
            "- ₹0.20/message (promotional)\n"
            "- ₹0.25/message (transactional)\n"
            "- ₹499/month basic plan"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []
    

class ActionPricingEmail(Action):
    def name(self) -> Text:
        return "action_pricing_email"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "💰 Email Pricing:\n"
            "- ₹0.10/email\n"
            "- ₹1499/month for up to 50,000 emails"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []

class ActionPricingChatbot(Action):
    def name(self) -> Text:
        return "action_pricing_chatbot"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "💰 Chatbot Pricing:\n"
            "- ₹1999/month (Standard Plan)\n"
            "- ₹4999/month (Pro Plan with integrations)"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Buttons
            buttons = [
                {"title": "🔙 Main Menu", "payload": "/main_menu"},
                {"title": "📅 Book a Demo", "payload": "/request_demo"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []    


#demo_form
class ActionAskName(Action):
    def name(self) -> Text:
        return "action_ask_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="👤 May I know your name?")
        return []
    
class ActionAskCompany(Action):
    def name(self) -> Text:
        return "action_ask_company"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="🏢 What's your company name?")
        return []

class ActionAskEmail(Action):
    def name(self) -> Text:
        return "action_ask_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="✉️ Please provide your email address.")
        return []

class ActionAskPhone(Action):
    def name(self) -> Text:
        return "action_ask_phone"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="📞 Could you share your phone number?")
        return []

class ActionAskService(Action):
    def name(self) -> Text:
        return "action_ask_service"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = "💼 Which service are you interested in?\n- WhatsApp\n- SMS\n- Email"

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "WhatsApp", "payload": "/service_whatsapp"},
                {"title": "SMS", "payload": "/service_sms"},
                {"title": "Email", "payload": "/service_email"},
                # {"title": "Chatbot", "payload": "/service_chatbot"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)
        return []
    
class ActionAskUseCase(Action):
    def name(self) -> Text:
        return "action_ask_use_case"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="🎯 What's your use case or goal with the service?")
        return []

class ActionAskPreferredTime(Action):
    def name(self) -> Text:
        return "action_ask_preferred_time"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "🕒 Please select a suitable time slot for the demo:\n"
            "- Morning (10 AM - 12 PM)\n"
            "- Afternoon (2 PM - 4 PM)\n"
            "- Evening (6 PM - 8 PM)"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)

        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "Morning (10 AM - 12 PM)", "payload": "/preferred_time_morning"},
                {"title": "Afternoon (2 PM - 4 PM)", "payload": "/preferred_time_afternoon"},
                {"title": "Evening (6 PM - 8 PM)", "payload": "/preferred_time_evening"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return []    

#support_form
class ActionAskSupportName(Action):
    def name(self) -> str:
        return "action_ask_support_name"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="👤 Please enter your full name:")
        return []

class ActionAskSupportEmail(Action):
    def name(self) -> str:
        return "action_ask_support_email"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="✉️ Please enter your email address:")
        return []

class ActionAskSupportCompany(Action):
    def name(self) -> str:
        return "action_ask_support_company"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="🏢 What's your company name?")
        return []

class ActionAskSupportPhone(Action):
    def name(self) -> str:
        return "action_ask_support_phone"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="📞 Please provide your phone number.")
        return []

class ActionAskSupportProduct(Action):
    def name(self) -> str:
        return "action_ask_support_product"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "Which product/service are you facing issues with?\n"
            "1. WhatsApp API\n"
            "2. SMS Service\n"
            "3. Email Service\n"
            "4. Chatbot"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "WhatsApp API", "payload": "/support_product_whatsapp"},
                {"title": "SMS Service", "payload": "/support_product_sms"},
                {"title": "Email Service", "payload": "/support_product_email"},
                # {"title": "Chatbot", "payload": "/support_product_chatbot"},
            ]
            dispatcher.utter_message(text="Which product/service are you facing issues with?", buttons=buttons)

        return []
    

class ActionAskSupportPriority(Action):
    def name(self) -> str:
        return "action_ask_support_priority"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "Please select the priority of your issue:\n"
            "1. High\n"
            "2. Medium\n"
            "3. Low"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "High", "payload": "/support_priority_high"},
                {"title": "Medium", "payload": "/support_priority_medium"},
                {"title": "Low", "payload": "/support_priority_low"}
            ]
            dispatcher.utter_message(text="Please select the priority of your issue:", buttons=buttons)

        return []
    
class ActionAskSupportQuery(Action):
    def name(self) -> str:
        return "action_ask_support_query"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="📝 Please describe your support query:")
        return []



#sales_form
class ActionAskSalesName(Action):
    def name(self) -> str:
        return "action_ask_sales_name"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="👤 Please enter your full name:")
        return []

class ActionAskSalesEmail(Action):
    def name(self) -> str:
        return "action_ask_sales_email"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="✉️ Please enter your email address:")
        return []

class ActionAskSalesCompany(Action):
    def name(self) -> str:
        return "action_ask_sales_company"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="🏢 What's your company name?")
        return []

class ActionAskSalesPhone(Action):
    def name(self) -> str:
        return "action_ask_sales_phone"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="📞 Please provide your phone number.")
        return []

class ActionAskSalesDesignation(Action):
    def name(self) -> str:
        return "action_ask_sales_designation"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "Please select your designation:\n"
            "1. Founder / Co-founder\n"
            "2. CEO / Director\n"
            "3. Marketing Manager\n"
            "4. IT Head / CTO\n"
            "5. Other"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "Founder / Co-founder", "payload": "/sales_designation_founder"},
                {"title": "CEO / Director", "payload": "/sales_designation_ceo"},
                {"title": "Marketing Manager", "payload": "/sales_designation_marketing"},
                {"title": "IT Head / CTO", "payload": "/sales_designation_it"},
                {"title": "Other", "payload": "/sales_designation_other"}
            ]
            dispatcher.utter_message(text="Please select your designation:", buttons=buttons)

        return []
    

class ActionAskSalesService(Action):
    def name(self) -> str:
        return "action_ask_sales_service"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "Which service are you interested in?\n"
            "1. WhatsApp API\n"
            "2. Bulk SMS\n"
            "3. Chatbot Development\n"
            "4. Bulk Email"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "WhatsApp API", "payload": "/sales_service_whatsapp"},
                {"title": "Bulk SMS", "payload": "/sales_service_sms"},
                {"title": "Chatbot Development", "payload": "/sales_service_chatbot"},
                {"title": "Bulk Email", "payload": "/sales_service_email"}
            ]
            dispatcher.utter_message(text="Which service are you interested in?", buttons=buttons)

        return []
    
class ActionAskSalesQuery(Action):
    def name(self) -> str:
        return "action_ask_sales_query"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        dispatcher.utter_message(text="📝 Please describe your sales inquiry:")
        return []

class ActionCustomerSupportMenu(Action):
    def name(self) -> str:
        return "action_customer_support_menu"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = (
            "How can we assist you today?\n"
            "1. 📩 Contact Support\n"
            "2. 💼 Contact Sales"
        )

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(text=message_text)
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "📩 Contact Support", "payload": "/contact_support"},
                {"title": "💼 Contact Sales", "payload": "/contact_sales"}
            ]
            dispatcher.utter_message(text="How can we assist you today?", buttons=buttons)

        return []

#demo_submit_form
class SubmitDemoForm(Action):
    def name(self) -> Text:
        return "action_submit_demo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("name")
        company = tracker.get_slot("company")
        email = tracker.get_slot("email")
        phone = tracker.get_slot("phone")
        service = tracker.get_slot("service")
        use_case = tracker.get_slot("use_case")
        preferred_time = tracker.get_slot("preferred_time")

        # Insert into DB
        insert_into_db(
            "INSERT INTO demo_requests (name, email, phone, company, service, use_case, preferred_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, email, phone, company, service, use_case, preferred_time)
        )

        dispatcher.utter_message(text="⌛ Please wait while I confirm your demo request...", pause=1.5)

        confirmation_text = f"""✅ Demo Confirmed!

        👤 Name: {name}  
        🏢 Company: {company}  
        ✉️ Email: {email}  
        📞 Phone: {phone}  
        💼 Service: {service}  
        🎯 Use Case: {use_case}  
        🕒 Preferred Time: {preferred_time}

        👉 Our team will contact you shortly.

        Would you like to continue?"""

        channel = tracker.get_latest_input_channel()

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(
                text=confirmation_text + "\n1. Back to Main Menu\n2. Exit\n(Please type your option)"
            )
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "🔙 Back to Main Menu", "payload": "/main_menu"},
                {"title": "❌ Exit", "payload": "/goodbye"}
            ]
            dispatcher.utter_message(text=confirmation_text, buttons=buttons)

        return [
            SlotSet("name", None),
            SlotSet("company", None),
            SlotSet("email", None),
            SlotSet("phone", None),
            SlotSet("service", None),
            SlotSet("use_case", None),
            SlotSet("preferred_time", None)
        ]


#support_submit_form
class ActionSubmitSupportForm(Action):
    def name(self) -> Text:
        return "action_submit_support_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> list:

        support_name = tracker.get_slot("support_name")
        support_email = tracker.get_slot("support_email")
        support_company = tracker.get_slot("support_company")
        support_phone = tracker.get_slot("support_phone")
        support_product = tracker.get_slot("support_product")
        support_priority = tracker.get_slot("support_priority")
        support_query = tracker.get_slot("support_query")

        channel = tracker.get_slot("user_channel")

        # Insert into DB
        insert_into_db(
            "INSERT INTO support_requests (name, email, company, phone, product, priority, query) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (support_name, support_email, support_company, support_phone, support_product, support_priority, support_query)
        )

        dispatcher.utter_message(text="📨 Submitting your support request...", pause=1.5)

        # Confirmation Summary Message
        confirmation_text = f"""✅ Support Request Submitted Successfully!

        👤 Name: {support_name}  
        ✉️ Email: {support_email}  
        🏢 Company: {support_company}  
        📞 Phone: {support_phone}  
        🛠️ Product/Service: {support_product}  
        🔔 Priority: {support_priority}  
        📝 Query: {support_query}

        📩 Our support team will get back to you shortly.
        """

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(
                text=confirmation_text + "\n1. Back to Main Menu\n2. Exit\n(Please type your option)"
            )
        else:
            buttons = [
                {"title": "🏠 Back to Main Menu", "payload": "/main_menu"},
                {"title": "❌ Exit", "payload": "/goodbye"}
            ]
            dispatcher.utter_message(text=confirmation_text, buttons=buttons)
        return [AllSlotsReset()]


#sales_submit_form
class ActionSubmitSalesForm(Action):
    def name(self) -> Text:
        return "action_submit_sales_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> list:

        sales_name = tracker.get_slot("sales_name")
        sales_email = tracker.get_slot("sales_email")
        sales_company = tracker.get_slot("sales_company")
        sales_phone = tracker.get_slot("sales_phone")
        sales_designation = tracker.get_slot("sales_designation")
        sales_service = tracker.get_slot("sales_service")
        sales_query = tracker.get_slot("sales_query")

        channel = tracker.get_slot("user_channel")

        # Insert into DB
        insert_into_db(
            "INSERT INTO sales_requests (name, email, company, phone, designation, service, query) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (sales_name, sales_email, sales_company, sales_phone, sales_designation, sales_service, sales_query)
        )

        dispatcher.utter_message(text="📨 Submitting your sales inquiry...", pause=1.5)

        # Confirmation Summary Message
        confirmation_text = f"""✅ Sales Inquiry Submitted Successfully!

        👤 Name: {sales_name}  
        ✉️ Email: {sales_email}  
        🏢 Company: {sales_company}  
        📞 Phone: {sales_phone}  
        🏷️ Designation: {sales_designation}  
        🛠️ Service Interested: {sales_service}  
        📝 Query: {sales_query}

        📞 Our sales team will reach out to you shortly.
        """

        if channel in ["instagram", "facebook"]:
            dispatcher.utter_message(
                text=confirmation_text + "\n\n1. Back to Main Menu\n2. Exit\n(Please type your option)"
            )
        else:
            # Telegram & other channels → buttons
            buttons = [
                {"title": "🏠 Back to Main Menu", "payload": "/main_menu"},
                {"title": "❌ Exit", "payload": "/goodbye"}
            ]
            dispatcher.utter_message(text=confirmation_text, buttons=buttons)

        return [AllSlotsReset()]



#services_store
class ActionLogExploreService(Action):
    def name(self) -> Text:
        return "action_log_explore_service"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message['intent'].get('name')
        service_map = {
            "service_whatsapp": "WhatsApp",
            "service_sms": "SMS",
            "service_email": "Email",
            "service_chatbot": "Chatbot"
        }
        service = service_map.get(intent)
        if service:
            insert_into_db("INSERT INTO explore_logs (service_name) VALUES (%s)", (service,))
        return []
    

#pricing_store
class ActionLogPricing(Action):
    def name(self) -> Text:
        return "action_log_pricing"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message['intent'].get('name')
        pricing_map = {
            "pricing_whatsapp": "WhatsApp",
            "pricing_sms": "SMS",
            "pricing_email": "Email",
            "pricing_chatbot": "Chatbot"
        }
        pricing_type = pricing_map.get(intent)
        if pricing_type:
            insert_into_db("INSERT INTO pricing_logs (pricing_type) VALUES (%s)", (pricing_type,))
        return []



#all_conversation_store
class ActionLogConversation(Action):
    def name(self) -> Text:
        return "action_log_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        session_id = tracker.sender_id
        channel_name = tracker.get_latest_input_channel()
        intent = tracker.latest_message.get('intent', {}).get('name', 'unknown')

        # Log User Message
        user_message = tracker.latest_message.get('text')
        if user_message:
            insert_into_db(
                "INSERT INTO conversation_logs (sender, message, session_id, intent_name, channel_name) VALUES (%s, %s, %s, %s, %s)",
                ('user', user_message, session_id, intent, channel_name)
            )

        # Log Bot Response (Get latest bot event)
        for event in reversed(tracker.events):
            if event.get('event') == 'bot':
                bot_message = event.get('text')
                if bot_message:
                    insert_into_db(
                        "INSERT INTO conversation_logs (sender, message, session_id, intent_name, channel_name) VALUES (%s, %s, %s, %s, %s)",
                        ('bot', bot_message, session_id, intent, channel_name)
                    )
                break  # Stop after logging latest bot response
        return []




#validation_step
class ValidateDemoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_demo_form"
    def validate_name(self, value: Text, dispatcher: CollectingDispatcher,
                  tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[A-Za-z ]{2,50}", value.strip()):
            return {"name": value.title()}
        dispatcher.utter_message(text="❌ Please enter a valid name using only letters.")
        return {"name": None}
    def validate_company(self, value: Text, dispatcher: CollectingDispatcher,
                     tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(value.strip()) >= 2:
            return {"company": value.strip()}
        dispatcher.utter_message(text="❌ Please enter a valid company name.")
        return {"company": None}
    def validate_email(self, value: Text, dispatcher: CollectingDispatcher,
                   tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[a-zA-Z]{2,}", value):
            return {"email": value.lower()}
        dispatcher.utter_message(text="❌ Please enter a valid email address.")
        return {"email": None}
    def validate_phone(self, value: Text, dispatcher: CollectingDispatcher,
                   tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if value.isdigit() and len(value) == 10 and value[0] in ['6', '7', '8', '9']:
            return {"phone": value}
        dispatcher.utter_message(text="❌ Invalid phone number. Must be 10 digits and start with 6, 7, 8, or 9.")
        return {"phone": None}
    
    # def validate_service(self, value: Text, dispatcher: CollectingDispatcher,
    #                  tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
    #     allowed_services = ["WhatsApp", "SMS", "Email", "Chatbot"]
    #     if value.capitalize() in allowed_services:
    #         return {"service": value.capitalize()}
    #     dispatcher.utter_message(text="❌ Please choose a valid service: WhatsApp, SMS, Email, or Chatbot.")
    #     return {"service": None}

    def validate_use_case(self, value: Text, dispatcher: CollectingDispatcher,
                      tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(value.strip()) >= 10:
            return {"use_case": value.strip()}
        dispatcher.utter_message(text="❌ Please provide more details about your use case (at least 10 characters).")
        return {"use_case": None}
    def validate_preferred_time(
        self, value: Text, dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        valid_slots = [
            "Morning (10 AM - 12 PM)",
            "Afternoon (2 PM - 4 PM)",
            "Evening (6 PM - 8 PM)"
        ]
        if value in valid_slots:
            return {"preferred_time": value}
        dispatcher.utter_message(text="❌ Please select a valid time slot from the given options.")
        return {"preferred_time": None}


class ValidateSupportForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_support_form"

    def validate_support_name(self, slot_value: Text, dispatcher: CollectingDispatcher,
                              tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[A-Za-z ]{3,50}", slot_value.strip()):
            return {"support_name": slot_value.title().strip()}
        dispatcher.utter_message(text="❌ Name must be at least 3 alphabetic characters.")
        return {"support_name": None}

    def validate_support_email(self, slot_value: Text, dispatcher: CollectingDispatcher,
                               tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[a-zA-Z]{2,}", slot_value):
            return {"support_email": slot_value.lower().strip()}
        dispatcher.utter_message(text="❌ Please enter a valid email address.")
        return {"support_email": None}

    def validate_support_company(self, slot_value: Text, dispatcher: CollectingDispatcher,
                                 tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(slot_value.strip()) >= 2:
            return {"support_company": slot_value.strip()}
        dispatcher.utter_message(text="❌ Company name can't be empty.")
        return {"support_company": None}
    
    def validate_support_phone(self, slot_value: Text, dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        if slot_value.isdigit() and len(slot_value) == 10:
            return {"support_phone": slot_value}
        dispatcher.utter_message(text="❌ Please enter a valid 10-digit phone number.")
        return {"support_phone": None}

    def validate_support_query(self, slot_value: Text, dispatcher: CollectingDispatcher,
                               tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(slot_value.strip()) >= 10:
            return {"support_query": slot_value.strip()}
        dispatcher.utter_message(text="❌ Query must be at least 10 characters.")
        return {"support_query": None}
    
    def validate_support_product(self, slot_value: Text, dispatcher: CollectingDispatcher,
                                 tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        allowed_products = ["WhatsApp API", "SMS Service", "Email Service", "Chatbot"]
        if slot_value in allowed_products:
            return {"support_product": slot_value}
        dispatcher.utter_message(text="❌ Please select a valid product/service option.")
        return {"support_product": None}

    def validate_support_priority(self, slot_value: Text, dispatcher: CollectingDispatcher,
                                  tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        allowed_priorities = ["High", "Medium", "Low"]
        if slot_value in allowed_priorities:
            return {"support_priority": slot_value}
        dispatcher.utter_message(text="❌ Please select a priority: High, Medium, or Low.")
        return {"support_priority": None}
    

    
    


class ValidateSalesForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sales_form"

    def validate_sales_name(self, slot_value: Text, dispatcher: CollectingDispatcher,
                            tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[A-Za-z ]{3,50}", slot_value.strip()):
            return {"sales_name": slot_value.title().strip()}
        dispatcher.utter_message(text="❌ Name must be at least 3 alphabetic characters.")
        return {"sales_name": None}

    def validate_sales_email(self, slot_value: Text, dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[a-zA-Z]{2,}", slot_value):
            return {"sales_email": slot_value.lower().strip()}
        dispatcher.utter_message(text="❌ Please enter a valid email address.")
        return {"sales_email": None}

    def validate_sales_company(self, slot_value: Text, dispatcher: CollectingDispatcher,
                               tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(slot_value.strip()) >= 2:
            return {"sales_company": slot_value.strip()}
        dispatcher.utter_message(text="❌ Company name can't be empty.")
        return {"sales_company": None}

    def validate_sales_query(self, slot_value: Text, dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if len(slot_value.strip()) >= 10:
            return {"sales_query": slot_value.strip()}
        dispatcher.utter_message(text="❌ Query must be at least 10 characters.")
        return {"sales_query": None}
    def validate_sales_phone(self, slot_value: Text, dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        if slot_value.isdigit() and len(slot_value) == 10:
            return {"sales_phone": slot_value}
        dispatcher.utter_message(text="❌ Please enter a valid 10-digit phone number.")
        return {"sales_phone": None}

    def validate_sales_designation(self, slot_value: Text, dispatcher: CollectingDispatcher,
                                   tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        if len(slot_value.strip()) >= 2:
            return {"sales_designation": slot_value.strip()}
        dispatcher.utter_message(text="❌ Please enter a valid designation (e.g., Manager, CEO).")
        return {"sales_designation": None}

    def validate_sales_service(self, slot_value: Text, dispatcher: CollectingDispatcher,
                               tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        allowed_services = ["WhatsApp API", "Bulk SMS", "Chatbot Development", "Bulk Email"]
        if slot_value in allowed_services:
            return {"sales_service": slot_value}
        dispatcher.utter_message(text="❌ Please select a valid service option.")
        return {"sales_service": None}

# today
class ActionExitFormMessage(Action):
    def name(self) -> Text:
        return "action_exit_form_message"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="🚪 start with fresh")
        return []


class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]

class ActionHandleDemoModuleInterrupt(Action):
    def name(self) -> Text:
        return "action_handle_demo_module_interrupt"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        channel = tracker.get_latest_input_channel()

        message_text = "📋 Welcome to the Demo Module Menu!"

        if channel in ["instagram", "facebook"]:
            # Instagram & Facebook → Only text
            dispatcher.utter_message(
                text=message_text + "\n1. Request Demo\n2. Main Menu\n(Please type your option)"
            )
        else:
            # Telegram & other channels → Text + Buttons
            buttons = [
                {"title": "📝 Request Demo", "payload": "/request_demo"},
                {"title": "🏠 Main Menu", "payload": "/main_menu"}
            ]
            dispatcher.utter_message(text=message_text, buttons=buttons)

        return [ActiveLoop(None), AllSlotsReset()]    

class ActionCustomFallback(Action):
    def name(self) -> Text:
        return "action_custom_fallback"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        active_form = tracker.active_loop.get("name")

        if active_form:
            dispatcher.utter_message(text="I didn’t understand that. Do you want to continue filling the form or exit?")
            buttons = [
                {"title": "Continue Form", "payload": "/affirm"},
                {"title": "Exit Form", "payload": "/exit_form"}
            ]
            dispatcher.utter_message(buttons=buttons)
        else:
            dispatcher.utter_message(text="Sorry, I didn’t get that. Please try again.")
            buttons = [
                {"title": "Go Back", "payload": "/main_menu"}  
            ]
            dispatcher.utter_message(buttons=buttons)

        return [UserUtteranceReverted()]

#feedback_store_in_database
class ActionStoreFeedback(Action):
    def name(self) -> Text:
        return "action_store_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message_id = tracker.get_slot("message_id")
        feedback_type = tracker.get_slot("feedback_type")
        feedback_text = tracker.get_slot("feedback_text")

        print(f"Feedback Received -> ID: {message_id}, Type: {feedback_type}, Text: {feedback_text}")

        # DB Insert Logic
        insert_into_db(
            "INSERT INTO feedback (message_id, feedback_type, feedback_text) VALUES (%s, %s, %s)",
            (message_id, feedback_type, feedback_text)
        )

        # Send Thank You Message as bot response
        dispatcher.utter_message(
            text="🙏 Thank you for your feedback! Would you like to go back to the main menu?",
        )
        return []
   
   
    #temporary
class ActionContinueChat(Action):
    def name(self) -> Text:
        return "action_continue_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="👍 You can continue from where you left off.")
        return []
    
class ActionRequestLiveAgent(Action):
    def name(self) -> Text:
        return "action_request_live_agent"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Connecting you to a live agent...")
        # Trigger Bridge API/WebSocket to notify agent (optional)
        return [SlotSet("live_agent", True)]
    
class ActionHandoverComplete(Action):
    def name(self) -> Text:
        return "action_handover_complete"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Bot is back online now!")
        return [SlotSet("live_agent", False)]

