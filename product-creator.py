# This script was used to create products

import stripe
from dotenv import load_dotenv
import os

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

basic_subscription = stripe.Product.create(
  name="Basic Subscription",
  description="$10/Month subscription",
)

basic_subscription_price = stripe.Price.create(
  unit_amount=1000,
  currency="usd",
  recurring={"interval": "month"},
  product=basic_subscription['id'],
)

pro_subscription = stripe.Product.create(
  name="Pro Subscription",
  description="$25/Month subscription",
)

pro_subscription_price = stripe.Price.create(
  unit_amount=2500,
  currency="usd",
  recurring={"interval": "month"},
  product=pro_subscription['id'],
)

enterprise_subscription = stripe.Product.create(
  name="Enterprise Subscription",
  description="$100/Month subscription",
)

enterprise_subscription_price = stripe.Price.create(
  unit_amount=10000,
  currency="usd",
  recurring={"interval": "month"},
  product=enterprise_subscription['id'],
)

# Save these identifiers

print(f"Success! Here is your basic subscription product id: {basic_subscription.id}") #prod_SjE8tPCX0xWJev
print(f"Success! Here is your basic subscription price id: {basic_subscription_price.id}") #price_1RnlfmFf4W5Y63k1EzAu467v
print(f"Success! Here is your pro subscription product id: {pro_subscription.id}") #prod_SjE8LHUt5ymK2Y
print(f"Success! Here is your pro subscription price id: {pro_subscription_price.id}") #price_1RnlfnFf4W5Y63k1fH2C40dP
print(f"Success! Here is your enterprise subscription product id: {enterprise_subscription.id}") #prod_SjE8St2lHiDjrd
print(f"Success! Here is your enterprise subscription price id: {enterprise_subscription_price.id}") #price_1RnlfnFf4W5Y63k1Y6VYsLoa
