// QUESTION: Is this sensitive? What is the web best practice to pass from backend to client side? Pass as Flask variable?
// Initialize stripe with test publishable key
const stripe = Stripe("pk_test_51RnNZyFf4W5Y63k1fz4nomxvdKPdjbmJteurjQoFFV3Qb9eWhW7fPgpLEcT6kvlvOBrpTKUGRRkQ2nMYfYPb34ks00jSBuExoU");

let checkout;

initialize();

const emailInput = document.getElementById("email");
const emailErrors = document.getElementById("email-errors");

const validateEmail = async (email) => {
  const updateResult = await checkout.updateEmail(email);
  const isValid = updateResult.type !== "error";

  return { isValid, message: !isValid ? updateResult.error.message : null };
};

document
  .querySelector("#payment-form")
  .addEventListener("submit", handleSubmit);

// Fetches a Checkout Session and captures the client secret
async function initialize() {

    // Get subscription option in the params
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString)
    const option = urlParams.get('option')
    const post_body = {'option' : option}

    // Call python endpoint that makes api call to Stripe to create Checkout Session and return Client Secret
    const promise = fetch("/create-checkout-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(post_body)
    })
    .then((r) => r.json())
    .then((r) => r.clientSecret)
    .catch(error => {
        // Show error message if there was a problem calling the Stripe API
        showErrorMessage('There was a problem loading the Stripe Payment Page. Please try again later.')
    })

    const appearance = {theme: 'stripe',};

    // Initialize Checkout => Returns checkout object (containing data from Checkout Session and methods to update it)
    checkout = await stripe.initCheckout({
        fetchClientSecret: () => promise, // promise contains client secret retrieved in main.py create checkout session
        elementsOptions: { appearance },
    });

    checkout.on('change', (session) => {
    // Handle changes to the checkout session
    });

    // Load the amount the customer should pay
    document.querySelector("#button-text").textContent = `Pay ${checkout.session().total.total.amount} now`;

    // Add email validators
    emailInput.addEventListener("input", () => {
        // Clear any validation errors
        emailErrors.textContent = "";
        emailInput.classList.remove("error");
    });

    emailInput.addEventListener("blur", async () => {
        const newEmail = emailInput.value;

        if (!newEmail) {
          return;
        }

        const { isValid, message } = await validateEmail(newEmail);

        if (!isValid) {
          emailInput.classList.add("error");
          emailErrors.textContent = message;
        }
    });

    // Update the Stripe payment form elements html
    const paymentElement = checkout.createPaymentElement();
    paymentElement.mount("#payment-element");
    const billingAddressElement = checkout.createBillingAddressElement();
    billingAddressElement.mount("#billing-address-element");

    // Update the "Your Cart" elements html
    const monthlyAmount = document.getElementById("monthly_amount");
    monthlyAmount.innerHTML = checkout.session().total.total.amount;
    const totalAmount = document.getElementById("total_amount");
    totalAmount.innerHTML = checkout.session().total.total.amount;
}

// When user clicks "Pay Now"
async function handleSubmit(e) {

  e.preventDefault();
  setLoading(true);

  const email = document.getElementById("email").value;
  const { isValid, message } = await validateEmail(email);

  if (!isValid) {
    emailInput.classList.add("error");
    emailErrors.textContent = message;
    showMessage(message);
    setLoading(false);
    return;
  }

  const { error } = await checkout.confirm();

  // This point will only be reached if there is an immediate error when
  // confirming the payment. Otherwise, your customer will be redirected to
  // your `return_url`. For some payment methods like iDEAL, your customer will
  // be redirected to an intermediate site first to authorize the payment, then
  // redirected to the `return_url`.
  showMessage(error.message);

  setLoading(false);
}

// ------- UI helpers -------

function showMessage(messageText) {
  const messageContainer = document.querySelector("#payment-message");

  messageContainer.classList.remove("hidden");
  messageContainer.textContent = messageText;

  setTimeout(function () {
    messageContainer.classList.add("hidden");
    messageContainer.textContent = "";
  }, 10000);
}

function showErrorMessage(messageText) {
  const messageContainer = document.querySelector("#error-message");

  messageContainer.classList.remove("hidden");
  messageContainer.textContent = messageText;

}

// Show a spinner on payment submission
function setLoading(isLoading) {
  if (isLoading) {
    // Disable the button and show a spinner
    document.querySelector("#submit").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.querySelector("#submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
}