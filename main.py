# pip3 install -r requirements.txt
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
import stripe
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

##################### Setup ########################

# Load variables from .env
load_dotenv()
LOCAL_DOMAIN = 'http://127.0.0.1:5001'

# Stripe Setup
stripe.api_key = os.getenv("STRIPE_API_KEY")
stripe.api_version = '2025-06-30.basil'

# Configure Flask App
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")

# Configure Bootstrap for app
bootstrap = Bootstrap5(app)

# Create the SQLAlchemy Database
class Base(DeclarativeBase):
  pass

# Create the Extension for the database
database = SQLAlchemy(model_class=Base)

# Configure the SQL database for the app in the instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///subscriptions.db"
# initialize the app with the extension
database.init_app(app)

# Create Model for database
class Subscription(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    subscription_id: Mapped[str] = mapped_column(String(100), unique=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    customer_email: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float)

# Create table schema in the database. Requires application context.
with app.app_context():
    database.create_all()

# TODO This should be way more dynamic. Use product lookup keys to find price id from server?
# Update the prices shown in index.html to show dynamic pricing
# most up to date product list? What is the best identifier for each product?
PRICE_LIST = {
    'Basic': 'price_1RnlfmFf4W5Y63k1EzAu467v',
    'Pro': 'price_1RnlfnFf4W5Y63k1fH2C40dP',
    'Enterprise': 'price_1RnlfnFf4W5Y63k1Y6VYsLoa'
}

##################### App Methods ########################

@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/complete')
def complete_page():
    return render_template("complete.html")

@app.route('/checkout', methods=['GET', 'POST'])
def checkout_page():

    try:
        subscription_option = request.args.get('option').title()
    except:
        subscription_option = 'Enterprise'
    finally:
        return render_template('checkout.html', option=subscription_option)

#
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """ Add an endpoint on your server that creates a Checkout Session, setting the ui_mode to custom.

    The Checkout Session response includes a client_secret, which the client uses to complete the payment.
    Return the client secret to the html in the response
    """
    # Get subscription option (i.e. basic, pro) from POST call
    data = request.get_json()
    product_option = data['option']

    # Get the corresponding price id (i.e. 'price_1RnlfmF..') from static list
    price_id = PRICE_LIST[product_option]

    try:
        # Create Checkout Session (New Session everytime customer attempts to pay)
        session = stripe.checkout.Session.create(
            ui_mode = 'custom',
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1
                },
            ],
            mode='subscription', # One or more recurring prices, use subscription

            # return_url=LOCAL_DOMAIN + '/complete.html?session_id={CHECKOUT_SESSION_ID}', # Not rendering when using .html ???
            return_url=LOCAL_DOMAIN + '/complete?session_id={CHECKOUT_SESSION_ID}',
        )

        # print(f'Session Details: {session}')

    except Exception as e:
        print('Exception thrown loading Stripe session')
        return str(e)

    # Pass client secret in URL so that when the user clicks "pay now" they can complete transaction
    return jsonify(clientSecret=session.client_secret)


@app.route('/session-status', methods=['GET'])
def session_status():
    """On re-route to checkout page, call method to get status of Stripe transaction

    If session status is "complete", create a Subscription record in the local database.

    Questions:
    1. Should Payment Intents be created using this type of Stripe Element?
    I am not seeing them created with this API.

    2. At what point should we reliably create the Subscription in the local db?
    Other docs look like they use webhooks just in case the internet/issues prevent user from successfully redirecting
    """

    session = stripe.checkout.Session.retrieve(request.args.get('session_id'), expand=["payment_intent"])

    if session.status == "complete":

      new_subscription = Subscription(
          subscription_id = session.subscription,
          session_id = session.id,
          customer_id = session.customer,
          customer_email = session.customer_details.email,
          amount = session.amount_total
      )

      database.session.add(new_subscription)
      database.session.commit()

    return jsonify(status=session.status, payment_status=session.payment_status)
    # return jsonify(status=session.status, payment_status=session.payment_status, payment_intent_id=session.payment_intent.id, payment_intent_status=session.payment_intent.status)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
