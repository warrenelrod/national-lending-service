import json
import streamlit as st
import streamlit.components.v1 as components

from utils import term_years, annual_rate


st.set_page_config(
    page_title="Mortgage Calculator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

credit_ranges = [
    "760+",
    "720-759",
    "680-719",
    "640-679",
    "600-639",
    "Below 600",
]

loan_types = ["Fixed", "FHA", "VA"]

rate_map = {
    str(term): {
        credit: annual_rate(term, credit)
        for credit in credit_ranges
    }
    for term in term_years
}

html = f"""
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <style>
    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      height: 100%;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, sans-serif;
      background:
        radial-gradient(
          ellipse 90% 100% at 80% 10%,
          rgba(150, 135, 255, 0.35) 0%,
          rgba(115, 95, 235, 0.22) 35%,
          rgba(70, 50, 170, 0.08) 65%,
          rgba(11, 8, 40, 0) 100%
        ),
        linear-gradient(
          180deg,
          #252377 0%,
          #24147f 34%,
          #171052 58%,
          #07051f 100%
        );
    }}

    .app {{
      width: 100%;
      max-width: 430px;
      height: 100dvh;
      margin: 0 auto;
      overflow-y: auto;
      overflow-x: hidden;
      scroll-snap-type: y mandatory;
      -webkit-overflow-scrolling: touch;
      padding: 0 1rem;
    }}

    .screen {{
      height: 100dvh;
      min-height: 100dvh;
      scroll-snap-align: start;
      scroll-snap-stop: always;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 1.25rem 0;
    }}

    .title {{
      padding-left: 0.6rem;
      padding-bottom: 0.5rem;
      color: white;
      font-family: Arial, Helvetica, sans-serif;
      letter-spacing: 1px;
      font-weight: 600;
      font-size: 44px;
      line-height: 1.1;
    }}

    .glass-card {{
      background: rgba(255, 255, 255, 0.74);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border-radius: 22px;
      padding: 1.25rem 1.1rem 1.45rem;
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.45),
        0 18px 45px rgba(25,25,110,0.20);
    }}

    .input-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 0.75rem;
      width: 100%;
    }}

    .field {{
      min-width: 0;
      margin-bottom: 0.95rem;
    }}

    label {{
      display: block;
      color: #151515;
      font-size: 0.95rem;
      font-weight: 750;
      margin-bottom: 0.35rem;
    }}

    input[type="number"],
    select {{
      width: 100%;
      min-width: 0;
      border: none;
      outline: none;
      background: rgba(255,255,255,0.84);
      color: #111;
      border-radius: 11px;
      padding: 0.55rem 0.6rem;
      font-size: 1rem;
      font-weight: 750;
    }}

    .pill-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-top: 0.35rem;
      margin-bottom: 1.1rem;
    }}

    .pill-stack {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}

    .pill-label {{
      color: #151515;
      font-size: 0.95rem;
      font-weight: 750;
      line-height: 1;
    }}

    .blue-pill {{
      background: #4C58F1;
      color: white;
      font-size: 1.25rem;
      font-weight: 850;
      padding: 0.45rem 0.7rem;
      border-radius: 11px;
      box-shadow: 0 3px 8px rgba(65,86,244,.32);
    }}

    .white-pill {{
      background: white;
      color: #111;
      font-size: 1.15rem;
      font-weight: 850;
      padding: 0.45rem 0.7rem;
      border-radius: 11px;
    }}

    input[type="range"] {{
      width: 100%;
      accent-color: #4C58F1;
    }}

    .payment-card {{
      background: rgba(255,255,255,0.9);
      border-radius: 24px;
      padding: 1.35rem 1.15rem;
      box-shadow: 0 14px 34px rgba(0,0,0,0.08);
      margin-top: 1.1rem;
    }}

    .payment-title {{
      font-size: 1rem;
      font-weight: 850;
      color: #111;
      margin-bottom: 0.25rem;
    }}

    .big-payment {{
      font-size: 3.8rem;
      line-height: 1;
      letter-spacing: -0.08em;
      font-weight: 500;
      color: #050505;
      margin-bottom: 0.65rem;
    }}

    .subtle {{
      color: #333;
      font-size: 0.95rem;
      margin-bottom: 0;
    }}

    .snap-hint {{
      text-align: center;
      color: rgba(255,255,255,.82);
      font-size: 0.82rem;
      margin-top: 1rem;
    }}

    @media (max-width: 360px) {{
      .glass-card {{
        padding-left: 0.8rem;
        padding-right: 0.8rem;
      }}

      .input-grid {{
        gap: 0.55rem;
      }}

      label {{
        font-size: 0.8rem;
      }}

      input[type="number"],
      select {{
        font-size: 0.92rem;
        padding-left: 0.45rem;
        padding-right: 0.45rem;
      }}

      .big-payment {{
        font-size: 3.35rem;
      }}
    }}
  </style>
</head>

<body>
  <main class="app">
    <section class="screen">
      <div class="title">Mortgage<br>Calculator</div>

      <div class="glass-card">
        <div class="input-grid">
          <div>
            <div class="field">
              <label for="loanAmount">Loan Amount</label>
              <input id="loanAmount" type="number" min="50000" max="3000000" step="5000" value="425000" />
            </div>

            <div class="field">
              <label for="creditRange">Credit Score</label>
              <select id="creditRange">
                {"".join(f'<option value="{c}">{c}</option>' for c in credit_ranges)}
              </select>
            </div>
          </div>

          <div>
            <div class="field">
              <label for="loanType">Loan Type</label>
              <select id="loanType">
                {"".join(f'<option value="{t}">{t}</option>' for t in loan_types)}
              </select>
            </div>

            <div class="field">
              <label for="loanTerm">Loan Term</label>
              <select id="loanTerm">
                {"".join(f'<option value="{t}" {"selected" if t == 30 else ""}>{t} years</option>' for t in term_years)}
              </select>
            </div>
          </div>
        </div>

        <div class="pill-row">
          <div class="pill-stack">
            <div class="pill-label">Down Payment</div>
            <div class="blue-pill" id="downPaymentDollars">$85,000</div>
          </div>
          <div class="white-pill" id="downPaymentPercent">20%</div>
        </div>

        <input id="downPaymentSlider" type="range" min="0" max="50" step="1" value="20" />

        <div class="payment-card">
          <div class="payment-title">Estimated Monthly Payment</div>
          <div class="big-payment" id="monthlyPayment">$2,234</div>
          <div class="subtle">principal + interest</div>
        </div>
      </div>

      <div class="snap-hint">Swipe up for payment ↑</div>
    </section>
  </main>

  <script>
    const rateMap = {json.dumps(rate_map)};

    const loanAmountEl = document.getElementById("loanAmount");
    const creditRangeEl = document.getElementById("creditRange");
    const loanTermEl = document.getElementById("loanTerm");
    const downPaymentSliderEl = document.getElementById("downPaymentSlider");

    const downPaymentDollarsEl = document.getElementById("downPaymentDollars");
    const downPaymentPercentEl = document.getElementById("downPaymentPercent");
    const monthlyPaymentEl = document.getElementById("monthlyPayment");

    const currency = new Intl.NumberFormat("en-US", {{
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0
    }});

    function monthlyPayment(principal, annualRate, years) {{
      const monthlyRate = annualRate / 100 / 12;
      const numberOfPayments = years * 12;

      if (monthlyRate === 0) {{
        return principal / numberOfPayments;
      }}

      return principal * (
        monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)
      ) / (
        Math.pow(1 + monthlyRate, numberOfPayments) - 1
      );
    }}

    function updateCalculator() {{
      const loanAmount = Number(loanAmountEl.value || 0);
      const creditRange = creditRangeEl.value;
      const loanTerm = Number(loanTermEl.value);
      const downPaymentPct = Number(downPaymentSliderEl.value);

      const downPayment = loanAmount * downPaymentPct / 100;
      const principal = loanAmount - downPayment;
      const annualRate = rateMap[String(loanTerm)][creditRange];
      const payment = monthlyPayment(principal, annualRate, loanTerm);

      downPaymentDollarsEl.textContent = currency.format(downPayment);
      downPaymentPercentEl.textContent = `${{downPaymentPct}}%`;
      monthlyPaymentEl.textContent = currency.format(payment);
    }}

    [
      loanAmountEl,
      creditRangeEl,
      loanTermEl,
      downPaymentSliderEl
    ].forEach((el) => {{
      el.addEventListener("input", updateCalculator);
      el.addEventListener("change", updateCalculator);
    }});

    updateCalculator();
  </script>
</body>
</html>
"""

components.html(html, height=900, scrolling=False)

















# principal_interest = monthly_payment(principal, interest_rate, loan_term)


# with st.container(key="result_section"):
#     st.markdown(
#         f"""
#         <div class="payment-card">
#             <div class="payment-title">Estimated Monthly Payment</div>
#             <div class="big-payment">${principal_interest:,.0f}</div>
#             <div class="subtle">principal + interest</div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     taxes_insurance = st.slider(
#         "Estimated taxes & insurance",
#         min_value=0,
#         max_value=2_000,
#         value=st.session_state.taxes_insurance,
#         step=25,
#         format="$%d",
#         key="taxes_insurance_widget",
#     )

#     total_monthly = principal_interest + taxes_insurance

#     st.markdown(
#         f"""
#             <div class="total">
#                 Total monthly <strong>~${total_monthly:,.0f}</strong><br>
#                 including taxes &amp; insurance
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     st.markdown('<div class="dark-hint">Swipe up for breakdown ↑</div>', unsafe_allow_html=True)


# with st.container(key="breakdown_section"):
#     total_interest = principal_interest * loan_term * 12 - principal
#     total_paid = principal + total_interest

#     st.markdown(
#         f"""
#         <div class="payment-card">
#             <div class="payment-title">Loan Breakdown</div>

#             <div class="metric-box">
#                 <div class="metric-label">Loan Principal</div>
#                 <div class="metric-value">${principal:,.0f}</div>
#             </div>

#             <div class="metric-box">
#                 <div class="metric-label">Down Payment</div>
#                 <div class="metric-value">${down_payment:,.0f}</div>
#             </div>

#             <div class="metric-box">
#                 <div class="metric-label">Total Interest</div>
#                 <div class="metric-value">${total_interest:,.0f}</div>
#             </div>

#             <div class="metric-box">
#                 <div class="metric-label">Total Principal + Interest</div>
#                 <div class="metric-value">${total_paid:,.0f}</div>
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     st.markdown('<div class="dark-hint">Swipe down to go back ↓</div>', unsafe_allow_html=True)
