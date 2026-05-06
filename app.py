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
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)


# -----------------------------
# Session state
# -----------------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False


# -----------------------------
# App styling
# -----------------------------
st.markdown(
    """
    <style>
        :root {
            --primary: #153A5B;
            --primary-dark: #0F2A42;
            --primary-soft: #EAF1F7;
            --accent: #C8953C;
            --accent-soft: #FFF4DF;
            --ink: #17202A;
            --muted: #5F6C7B;
            --line: #D9E1EA;
            --card: #FFFFFF;
            --success-bg: #EAF7EF;
            --error-bg: #FDECEC;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(200, 149, 60, 0.16), transparent 34rem),
                linear-gradient(180deg, #F7FAFD 0%, #EEF4F8 100%);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: rgba(247, 250, 253, 0.82);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(217, 225, 234, 0.6);
        }

        [data-testid="stToolbar"] {
            right: 1.25rem;
        }

        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 3.5rem;
        }

        h1 {
            color: var(--primary-dark);
            letter-spacing: -0.045em;
            font-size: clamp(2.1rem, 4vw, 3.25rem) !important;
            line-height: 1.04 !important;
            margin-bottom: 0.35rem !important;
        }

        h2, h3 {
            color: var(--primary-dark);
            letter-spacing: -0.025em;
        }

        h2 {
            font-size: 1.45rem !important;
            margin-top: 0.3rem !important;
        }

        h3 {
            font-size: 1.25rem !important;
        }

        p, label, span, div {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .hero-card {
            background:
                linear-gradient(135deg, rgba(21, 58, 91, 0.98), rgba(15, 42, 66, 0.96)),
                radial-gradient(circle at top right, rgba(200, 149, 60, 0.34), transparent 22rem);
            border-radius: 28px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.22);
            box-shadow: 0 24px 70px rgba(21, 58, 91, 0.18);
            margin-top: 1.4rem;
            margin-bottom: 1.4rem;
        }

        .hero-eyebrow {
            color: #F3D8A2;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.75rem;
            font-weight: 800;
            margin-bottom: 0.65rem;
        }

        .hero-title {
            color: #FFFFFF;
            font-size: clamp(2.15rem, 5vw, 3.65rem);
            line-height: 1;
            letter-spacing: -0.055em;
            font-weight: 850;
            margin-bottom: 0.8rem;
        }

        .hero-subtitle {
            color: rgba(255, 255, 255, 0.82);
            max-width: 700px;
            font-size: 1.02rem;
            line-height: 1.65;
            margin-bottom: 1.15rem;
        }

        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            color: #FFFFFF;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 999px;
            padding: 0.42rem 0.75rem;
            font-size: 0.82rem;
            font-weight: 650;
        }

        .disclosure-card {
            background: rgba(255, 244, 223, 0.72);
            border: 1px solid rgba(200, 149, 60, 0.34);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            color: #5A4319;
            line-height: 1.55;
            margin-bottom: 1.25rem;
        }

        .section-shell {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(217, 225, 234, 0.88);
            border-radius: 26px;
            padding: 1.35rem;
            box-shadow: 0 18px 50px rgba(21, 58, 91, 0.08);
            margin: 1.2rem 0;
        }

        .section-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: var(--primary);
            background: var(--primary-soft);
            border: 1px solid rgba(21, 58, 91, 0.1);
            border-radius: 999px;
            padding: 0.5rem 0.7rem;
            font-size: 0.78rem;
            font-weight: 780;
            margin-bottom: 0.0rem;
        }

        .section-copy {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.6;
            margin-top: -0.35rem;
            margin-bottom: 0.0rem;
        }

        .result-panel {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(234, 241, 247, 0.82));
            border: 1px solid rgba(21, 58, 91, 0.13);
            border-radius: 26px;
            padding: 1.25rem;
            margin-top: 1rem;
            box-shadow: 0 18px 54px rgba(21, 58, 91, 0.11);
        }

        .result-title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: -1.0rem;
        }

        .rate-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: var(--accent-soft);
            color: #6A4610;
            border: 1px solid rgba(200, 149, 60, 0.28);
            padding: 0.45rem 0.8rem;
            font-size: 0.82rem;
            font-weight: 780;
        }

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid rgba(217, 225, 234, 0.92);
            border-radius: 20px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 10px 30px rgba(21, 58, 91, 0.06);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-weight: 720;
        }

        [data-testid="stMetricValue"] {
            color: var(--primary-dark);
            font-weight: 850;
            letter-spacing: -0.035em;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea {
            border-radius: 14px !important;
            border-color: rgba(21, 58, 91, 0.18) !important;
            background-color: #FFFFFF !important;
        }

        div[data-baseweb="input"]:focus-within > div,
        div[data-baseweb="select"]:focus-within > div,
        textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(200, 149, 60, 0.18) !important;
        }

        .stNumberInput label,
        .stTextInput label,
        .stTextArea label,
        .stSelectbox label,
        .stCheckbox label {
            color: var(--primary-dark) !important;
            font-weight: 720 !important;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            width: 100%;
            border-radius: 999px;
            border: 1px solid rgba(21, 58, 91, 0.15);
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: #FFFFFF;
            font-weight: 820;
            padding: 0.72rem 1rem;
            box-shadow: 0 12px 26px rgba(21, 58, 91, 0.18);
            transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            border-color: rgba(200, 149, 60, 0.65);
            color: #FFFFFF;
            filter: brightness(1.05);
            transform: translateY(-1px);
            box-shadow: 0 16px 30px rgba(21, 58, 91, 0.22);
        }

        div.stButton > button:active,
        div.stFormSubmitButton > button:active {
            transform: translateY(0);
            box-shadow: 0 8px 18px rgba(21, 58, 91, 0.15);
        }

        .stAlert {
            border-radius: 18px;
            border: 1px solid rgba(21, 58, 91, 0.08);
        }

        hr {
            margin: 1.8rem 0 !important;
            border-color: rgba(217, 225, 234, 0.85) !important;
        }

        .footer-note {
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(217, 225, 234, 0.75);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.55;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.35rem;
            }

            .hero-card {
                padding: 1.35rem;
                border-radius: 22px;
            }

            .section-shell,
            .result-panel {
                padding: 1rem;
                border-radius: 22px;
            }

            [data-testid="stMetric"] {
                padding: 0.9rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helper functions
# -----------------------------
def is_mobile_user() -> bool:
    try:
        user_agent = st.context.headers.get("user-agent", "").lower()
    except Exception:
        user_agent = ""

    mobile_keywords = [
        "iphone",
        "android",
        "ipad",
        "mobile",
        "blackberry",
        "windows phone",
    ]

    return any(keyword in user_agent for keyword in mobile_keywords)


def scroll_to(element_id):
    js = f"""
    <script>
        setTimeout(function() {{
            const target = document.getElementById("{element_id}");

            if (target) {{
                target.scrollIntoView({{
                    behavior: "smooth",
                    block: "start"
                }});
            }}
        }}, 100);
    </script>
    """

    st.html(js, unsafe_allow_javascript=True)


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

    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


# -----------------------------
# Branding / compliance placeholders
# -----------------------------
MLO_NAME = "Your MLO Name"
COMPANY_NAME = "Your Mortgage Company"
NMLS_ID = "NMLS #XXXXXXX"
FL_LICENSE = "Florida License #XXXXXXX"
SERVICE_AREA = "Pinellas County and surrounding Florida communities"


# ---------------------------------------------------------------------------------------------------------------------
# Header

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-eyebrow">Mortgage payment estimate</div>
        <div class="hero-title">Pinellas Mortgage Calculator</div>
        <div class="hero-subtitle">
            Estimate a monthly mortgage payment, then request a consultation with a licensed loan originator
            serving {SERVICE_AREA}.
        </div>
        <div class="hero-badges">
            <div class="hero-badge">🏢 {COMPANY_NAME}</div>
            <div class="hero-badge">👤 {MLO_NAME}</div>
            <div class="hero-badge">📋 {NMLS_ID}</div>
            <div class="hero-badge">📍 {FL_LICENSE}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="disclosure-card">
        <strong>Educational estimate only.</strong>
        This calculator is not a loan approval, loan estimate, commitment to lend, or advertisement of a locked
        interest rate. Final terms depend on credit, income, assets, property, loan program, and underwriting.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------------------------------------------------
# Calculator

is_mobile = is_mobile_user()

st.markdown(
    """
    <div class="section-shell">
        <div class="section-kicker">Calculator</div>
        <h2>Mortgage Payment Estimate</h2>
        <div class="section-copy">
            Adjust the purchase price, down payment, loan term, and estimated credit range to preview a payment.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")

with col1:
    purchase_price = st.number_input(
        "Purchase price",
        min_value=0.0,
        value=450000.0,
        step=5000.0,
        format="%.2f",
    )

    down_col1, down_col2 = st.columns([2, 1])

    with down_col1:
        down_payment_percent = st.number_input(
            "Down payment %",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            format="%.2f",
        )

    with down_col2:
        down_payment_amount_preview = purchase_price * down_payment_percent / 100

        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: flex-end;
                height: 72px;
                padding-bottom: 0.45rem;
                font-weight: 800;
                color: #153A5B;
                letter-spacing: -0.02em;
            ">
                {format_currency(down_payment_amount_preview)}
            </div>
            """,
            unsafe_allow_html=True,
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
        ],
    )

if is_mobile or st.session_state.submitted == False:
    submitted_calc = st.button("Calculate payment")
    if submitted_calc:
        st.session_state.submitted = True
        if not is_mobile:
            st.rerun()


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

monthly_pmi = 0 if down_payment_percent >= 20.0 else (loan_amount * 0.008) / 12

monthly_pi = calculate_monthly_pi(loan_amount, annual_rate, loan_term_years)
estimated_total_payment = monthly_pi + monthly_pmi


if st.session_state.submitted:
    if is_mobile:
        st.session_state.submitted = False

    element_id = "results-scroll-target"

    st.markdown(
        f"""
        <div id="{element_id}" style="height: 1px; scroll-margin-top: 72px;"></div>
        <div class="result-panel">
            <div class="result-title-row">
                <div>
                    <div class="section-kicker">Results</div>
                    <h2 style="margin-bottom: 0;">Estimated Monthly Payment</h2>
                </div>
                <div class="rate-pill">Estimated rate: {annual_rate:.3f}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    scroll_to(element_id)

    metric_cols = st.columns(3, gap="small")
    metric_cols[0].metric("Loan amount", format_currency(loan_amount))
    metric_cols[1].metric("Down payment", format_currency(down_payment_amount))
    metric_cols[2].metric("Estimated Interest Rate", f"{annual_rate} %")

    metric_cols_2 = st.columns(3, gap="small")
    metric_cols_2[0].metric("Principal & interest", format_currency(monthly_pi))
    metric_cols_2[1].metric("Estimated PMI / MI", format_currency(monthly_pmi))
    metric_cols_2[2].metric("Estimated total monthly payment", format_currency(estimated_total_payment))


# ---------------------------------------------------------------------------------------------------------------------
# Lead submission form

st.divider()

st.markdown(
    f"""
    <div class="section-shell">
        <div class="section-kicker">Consultation request</div>
        <h2>Request a Mortgage Consultation</h2>
        <div class="section-copy">
            Submit your information and a licensed loan originator serving {SERVICE_AREA} will follow up.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("lead_form", clear_on_submit=False):
    lead_col1, lead_col2 = st.columns(2, gap="large")

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
Estimated purchase price / home value: {format_currency(target_price)}
Estimated credit range: {credit_range}

CALCULATOR SNAPSHOT
Purchase price used: {format_currency(purchase_price)}
Down payment: {down_payment_percent:.2f}% / {format_currency(down_payment_amount)}
Estimated loan amount: {format_currency(loan_amount)}
Interest rate used: {annual_rate:.3f}%
Loan term: {loan_term_years} years
Principal & interest: {format_currency(monthly_pi)}
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
                "Please check the SMTP configuration."
            )
            st.exception(exc)


# ---------------------------------------------------------------------------------------------------------------------
# Footer disclosures

st.divider()

st.markdown(
    f"""
    <div class="footer-note">
        {COMPANY_NAME} | {MLO_NAME} | {NMLS_ID} | {FL_LICENSE}. Licensed mortgage activity is subject to
        applicable federal and Florida law. Calculator results are estimates only and do not include all possible
        costs, fees, escrows, points, lender credits, APR, prepaid items, flood insurance, condo assessments,
        or program-specific mortgage insurance.
    </div>
    """,
    unsafe_allow_html=True,
)
