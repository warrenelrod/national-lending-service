from datetime import datetime

import smtplib
import ssl
import streamlit as st
from email.message import EmailMessage

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Pinellas Mortgage Calculator",
    page_icon="🏠",
    layout="centered",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None,
    }
)


# -----------------------------
# Helper functions
# -----------------------------
def calculate_monthly_pi(loan_amount: float, annual_rate: float, years: int) -> float:
    """
    Principal + interest monthly payment.
    """
    if loan_amount <= 0 or years <= 0:
        return 0.0

    monthly_rate = annual_rate / 100 / 12
    number_payments = years * 12

    if monthly_rate == 0:
        return loan_amount / number_payments

    payment = loan_amount * (
        monthly_rate * (1 + monthly_rate) ** number_payments
    ) / (
        (1 + monthly_rate) ** number_payments - 1
    )

    return payment


def estimate_interest_rate_from_pi(
    loan_amount: float,
    monthly_pi: float,
    years: int,
    low_rate: float = 0.0,
    high_rate: float = 20.0,
    tolerance: float = 0.00001,
    max_iterations: int = 100
) -> float:
    """
    Estimate annual interest rate from loan amount, monthly P&I payment, and term.
    Uses binary search because the mortgage formula is hard to rearrange directly.
    Returns annual interest rate as a percentage.
    """

    if loan_amount <= 0 or monthly_pi <= 0 or years <= 0:
        return 0.0

    number_payments = years * 12

    # If payment is basically a 0% interest payment
    zero_interest_payment = loan_amount / number_payments
    if monthly_pi <= zero_interest_payment:
        return 0.0

    low = low_rate
    high = high_rate

    for _ in range(max_iterations):
        mid = (low + high) / 2
        estimated_payment = calculate_monthly_pi(loan_amount, mid, years)

        if abs(estimated_payment - monthly_pi) < tolerance:
            return mid

        if estimated_payment < monthly_pi:
            low = mid
        else:
            high = mid

    return (low + high) / 2


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def send_email(subject: str, body: str, reply_to: str | None = None) -> None:
    """
    Sends email using SMTP credentials from Streamlit secrets.
    Required secrets:
      SMTP_HOST
      SMTP_PORT
      SMTP_USERNAME
      SMTP_PASSWORD
      FROM_EMAIL
      TO_EMAIL
    """
    smtp_host = st.secrets["SMTP_HOST"]
    smtp_port = int(st.secrets["SMTP_PORT"])
    smtp_username = st.secrets["SMTP_USERNAME"]
    smtp_password = st.secrets["SMTP_PASSWORD"]
    from_email = st.secrets["FROM_EMAIL"]
    to_email = st.secrets["TO_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    if reply_to:
        msg["Reply-To"] = reply_to

    msg.set_content(body)

    context = ssl.create_default_context()

    # # TODO: ---------------------------------------------------------------------------------------------------------
    # with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
    #     server.login(smtp_username, smtp_password)
    #     server.send_message(msg)


# -----------------------------
# Branding / compliance placeholders
# -----------------------------
MLO_NAME = "Your MLO Name"
COMPANY_NAME = "Your Mortgage Company"
NMLS_ID = "NMLS #XXXXXXX"
FL_LICENSE = "Florida License #XXXXXXX"
SERVICE_AREA = "Pinellas County and surrounding Florida communities"


# -----------------------------
# Header
# -----------------------------
st.title("🏠 Pinellas Mortgage Calculator")
st.caption(f"{COMPANY_NAME} | {MLO_NAME} | {NMLS_ID} | {FL_LICENSE}")

st.info(
    "This calculator is for educational estimates only. It is not a loan approval, "
    "loan estimate, commitment to lend, or advertisement of a locked interest rate. "
    "Final terms depend on credit, income, assets, property, loan program, and underwriting."
)


# 1. Initialize session state to track if the form was submitted
if "submitted" not in st.session_state:
    st.session_state.submitted = False


# -----------------------------
# Calculator
# -----------------------------
st.header("Mortgage Payment Estimate")

with st.form("mortgage_calculator"):
    col1, col2 = st.columns(2)

    with col1:
        purchase_price = st.number_input(
            "Purchase price",
            min_value=0.0,
            value=450000.0,
            step=5000.0,
            format="%.2f",
        )

        down_payment_percent = st.number_input(
            "Down payment %",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            format="%.2f",
        )

    with col2:
        loan_term_years = st.selectbox(
            "Loan term",
            options=[30, 15],
            index=0,
        )

        credit_range = st.selectbox(
            "Estimated credit score range",
            options=[
                "760+",
                "720-759",
                "680-719",
                "640-679",
                "600-639",
                "Below 600",
            ]
        )

    submitted_calc = st.form_submit_button("Calculate payment")

    if submitted_calc:
        st.session_state.submitted = True


credit_mapping = {
    30: {
        "760+": 6.32,
        "720-759": 6.36,
        "680-719": 6.41,
        "640-679": 6.46,
        "600-639": 6.50,
        "Below 600": 6.54,
    },
    15: {
        "760+": 5.50,
        "720-759": 5.55,
        "680-719": 5.60,
        "640-679": 5.65,
        "600-639": 5.70,
        "Below 600": 5.75,
    }
}

annual_rate = credit_mapping[loan_term_years][credit_range]

down_payment_amount = purchase_price * down_payment_percent / 100
loan_amount = max(purchase_price - down_payment_amount, 0)

monthly_pmi = (loan_amount * 0.008) / 12

monthly_pi = calculate_monthly_pi(loan_amount, annual_rate, loan_term_years)
estimated_total_payment = monthly_pi + monthly_pmi









# 3. Target subheader with a unique anchor
if st.session_state.submitted:
    st.session_state.submitted = False

    st.markdown(
        """
        <div id="results-scroll-target"></div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Estimated Monthly Payment")

    js = """
    <script>
        setTimeout(function() {
            const doc = window.parent.document;
            const target = doc.getElementById("results-scroll-target");

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }, 400);
    </script>
    """

    st.iframe(js, height=1)


    metric_cols = st.columns(3)
    metric_cols[0].metric("Loan amount", format_currency(loan_amount))
    metric_cols[1].metric("Down payment", format_currency(down_payment_amount))
    metric_cols[2].metric("Estimated Interest Rate", f"{annual_rate} %")

    metric_cols_2 = st.columns(3)
    metric_cols_2[0].metric("Principal & interest", format_currency(monthly_pi))
    metric_cols_2[1].metric("Estimated PMI / MI", format_currency(monthly_pmi))
    metric_cols_2[2].metric("Estimated total monthly payment", format_currency(estimated_total_payment))























# -----------------------------
# Lead submission form
# -----------------------------
st.divider()
st.header("Request a Mortgage Consultation")

st.write(
    f"Submit your information and a licensed loan originator serving {SERVICE_AREA} "
    "will follow up."
)

with st.form("lead_form", clear_on_submit=False):
    lead_col1, lead_col2 = st.columns(2)

    with lead_col1:
        first_name = st.text_input("First name *")
        last_name = st.text_input("Last name *")
        email = st.text_input("Email *")
        phone = st.text_input("Phone *")

    with lead_col2:
        loan_purpose = st.selectbox(
            "Loan purpose *",
            options=[
                "Purchase",
                "Refinance",
                "Cash-out refinance",
                "HELOC / second mortgage",
                "Not sure yet"
            ]
        )

        property_location = st.text_input(
            "Property city / county",
            value="Pinellas County, FL"
        )

        target_price = st.number_input(
            "Estimated purchase price or home value",
            min_value=0.0,
            value=float(purchase_price),
            step=5000.0,
            format="%.2f"
        )

        timeframe = st.selectbox(
            "Timeframe",
            options=[
                "Immediately",
                "Next 30 days",
                "1-3 months",
                "3-6 months",
                "Just researching"
            ]
        )

    credit_range = st.selectbox(
        "Estimated credit score range",
        options=[
            "760+",
            "720-759",
            "680-719",
            "640-679",
            "600-639",
            "Below 600",
            "Not sure / prefer not to say"
        ]
    )

    message = st.text_area(
        "Anything else you want the MLO to know?",
        placeholder="Example: first-time buyer, VA loan, condo, self-employed, relocating, etc."
    )

    consent = st.checkbox(
        "I consent to be contacted by phone, email, or text about mortgage financing. "
        "Message/data rates may apply. I understand this is not a loan application or approval."
    )

    submit_lead = st.form_submit_button("Submit request")


if submit_lead:
    required_fields = {
        "First name": first_name,
        "Last name": last_name,
        "Email": email,
        "Phone": phone,
    }

    missing = [field for field, value in required_fields.items() if not value.strip()]

    if missing:
        st.error(f"Please complete: {', '.join(missing)}")
    elif not consent:
        st.error("Please provide contact consent before submitting.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = f"New mortgage lead: {first_name} {last_name} - {loan_purpose}"

        email_body = f"""
New mortgage lead submitted from Streamlit portal.

Submitted at: {timestamp}

CONTACT
Name: {first_name} {last_name}
Email: {email}
Phone: {phone}

LOAN DETAILS
Loan purpose: {loan_purpose}
Property location: {property_location}
Timeframe: {timeframe}
Estimated purchase price / home value: {format_currency(target_price)}
Estimated credit range: {credit_range}

CALCULATOR SNAPSHOT
Purchase price used: {format_currency(purchase_price)}
Down payment: {down_payment_percent:.2f}% / {format_currency(down_payment_amount)}
Estimated loan amount: {format_currency(loan_amount)}
Interest rate used: {annual_rate:.3f}%
Loan term: {loan_term_years} years
Principal & interest: {format_currency(monthly_pi)}
Estimated taxes: {format_currency(monthly_tax)} / month
PMI / MI: {format_currency(monthly_pmi)} / month
Estimated total monthly payment: {format_currency(estimated_total_payment)}

BORROWER MESSAGE
{message if message.strip() else "No additional message provided."}

COMPLIANCE NOTE
The borrower consented to be contacted and acknowledged this is not a loan application or approval.
"""

        try:
            send_email(
                subject=subject,
                body=email_body,
                reply_to=email
            )
            st.success(
                "Your request was submitted successfully. A licensed mortgage professional will follow up."
            )
        except Exception as exc:
            st.error(
                "The form was completed, but the email could not be sent. "
                # "Please check the SMTP configuration."
            )
            st.exception(exc)


# -----------------------------
# Footer disclosures
# -----------------------------
st.divider()

st.caption(
    f"{COMPANY_NAME} | {MLO_NAME} | {NMLS_ID} | {FL_LICENSE}. "
    "Licensed mortgage activity is subject to applicable federal and Florida law. "
    "Calculator results are estimates only and do not include all possible costs, fees, escrows, "
    "points, lender credits, APR, prepaid items, flood insurance, condo assessments, or program-specific mortgage insurance."
)
