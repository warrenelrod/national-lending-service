import json
import streamlit as st

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

DEFAULT_LOAN_AMOUNT = 425_000
DEFAULT_CREDIT_RANGE = "760+"
DEFAULT_LOAN_TYPE = "Fixed"
DEFAULT_LOAN_TERM = 30
DEFAULT_DOWN_PAYMENT_PCT = 20

rate_map = {
    str(term): {
        credit: annual_rate(term, credit)
        for credit in credit_ranges
    }
    for term in term_years
}


def option_tags(options, selected=None, label_fn=str):
    return "".join(
        f'<option value="{option}" {"selected" if option == selected else ""}>'
        f"{label_fn(option)}"
        "</option>"
        for option in options
    )


st.markdown(
    """
    <style>
      * {
        box-sizing: border-box;
      }

      :root {
        --app-bg:
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

        --field-bg: rgba(255,255,255,0.84);
        --field-radius: 11px;
        --field-height: 2.45rem;
      }

      html,
      body,
      #root {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100% !important;
        background: #07051f !important;
        overflow-x: hidden !important;
      }

      body {
        overscroll-behavior-y: none;
      }

      .stApp,
      .snap-app,
      section.stAppViewMain,
      section.main,
      section[data-testid="stMain"],
      div[data-testid="stAppViewContainer"] > section {
        background: var(--app-bg) !important;
      }

      header,
      footer,
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"] {
        display: none !important;
      }

      .block-container,
      [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
        width: 100% !important;
      }

      section.stAppViewMain,
      section.main,
      section[data-testid="stMain"],
      div[data-testid="stAppViewContainer"] > section {
        height: 100svh !important;
        max-height: 100svh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        scroll-snap-type: y mandatory !important;
        scroll-padding: 0 !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-y: contain !important;
      }

      .snap-app {
        width: 100%;
        min-height: 200svh;
      }

      .snap-page {
        width: 100%;
        min-height: 100svh;
        scroll-snap-align: start;
        scroll-snap-stop: always;

        display: flex;
        justify-content: center;
        align-items: center;

        padding:
          max(1rem, env(safe-area-inset-top))
          1rem
          max(1.25rem, env(safe-area-inset-bottom));
      }

      .phone-width {
        width: 100%;
        max-width: 430px;
      }

      .title {
        padding-left: 0.6rem;
        padding-bottom: 0.5rem;
        color: white;
        font-family: Arial, Helvetica, sans-serif;
        letter-spacing: 1px;
        font-weight: 600;
        font-size: 44px;
        line-height: 1.1;
      }

      .glass-card {
        background: rgba(255, 255, 255, 0.74);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 22px;
        padding: 1.25rem 1.1rem 1.45rem;
        box-shadow:
          inset 0 1px 0 rgba(255,255,255,0.45),
          0 18px 45px rgba(25,25,110,0.20);
      }

      .input-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
        gap: 0.75rem;
        width: 100%;
      }

      .field {
        min-width: 0;
        margin-bottom: 0.95rem;
      }

      label {
        display: block;
        color: #151515;
        font-size: 0.95rem;
        font-weight: 750;
        margin-bottom: 0.35rem;
      }

      input[type="text"],
      select {
        width: 100%;
        min-width: 0;
        height: var(--field-height);
        border: none;
        outline: none;
        background: var(--field-bg);
        color: #111;
        border-radius: var(--field-radius);
        padding: 0.55rem 0.6rem;
        font-size: 1rem;
        line-height: 1.2;
        font-weight: 750;
        user-select: auto;
      }

      input[type="text"] {
        appearance: none;
        -webkit-appearance: none;
      }

      .pill-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-top: 0.35rem;
        margin-bottom: 1.1rem;
      }

      .pill-stack {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }

      .pill-label {
        color: #151515;
        font-size: 0.95rem;
        font-weight: 750;
        line-height: 1;
      }

      .blue-pill,
      .white-pill {
        font-weight: 850;
        padding: 0.45rem 0.7rem;
        border-radius: var(--field-radius);
      }

      .blue-pill {
        background: #4C58F1;
        color: white;
        font-size: 1.25rem;
        box-shadow: 0 3px 8px rgba(65,86,244,.32);
      }

      .white-pill {
        background: white;
        color: #111;
        font-size: 1.15rem;
      }

      input[type="range"] {
        width: 100%;
        accent-color: #4C58F1;
      }

      .payment-card {
        background: rgba(255,255,255,0.9);
        border-radius: 24px;
        padding: 1.35rem 1.15rem;
        box-shadow: 0 14px 34px rgba(0,0,0,0.08);
        margin-top: 1.1rem;
      }

      .payment-title {
        font-size: 1rem;
        font-weight: 850;
        color: #111;
        margin-bottom: 0.25rem;
      }

      .big-payment {
        font-size: 3.8rem;
        line-height: 1;
        letter-spacing: -0.08em;
        font-weight: 500;
        color: #050505;
        margin-bottom: 0.65rem;
      }

      .subtle {
        color: #333;
        font-size: 0.95rem;
        margin-bottom: 0;
      }

      .snap-hint {
        text-align: center;
        color: rgba(255,255,255,.82);
        font-size: 0.82rem;
        margin-top: 1rem;
      }

      .dummy-page {
        color: white;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, sans-serif;
      }

      .dummy-page h2 {
        font-size: 2.25rem;
        margin: 0 0 0.75rem;
      }

      .dummy-page p {
        margin: 0;
        color: rgba(255,255,255,.78);
      }

      @media (max-width: 360px) {
        .glass-card {
          padding-left: 0.8rem;
          padding-right: 0.8rem;
        }

        .input-grid {
          gap: 0.55rem;
        }

        label {
          font-size: 0.8rem;
        }

        input[type="text"],
        select {
          font-size: 0.92rem;
          padding-left: 0.45rem;
          padding-right: 0.45rem;
        }

        .big-payment {
          font-size: 3.35rem;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


html = f"""
<div class="snap-app">

  <section class="snap-page">
    <div class="phone-width dummy-page">
      <h2>Landing Page</h2>
      <p>Dummy page.</p>
      <div class="snap-hint">Swipe up for more info↑</div>
    </div>
  </section>

  <section class="snap-page">
    <div class="phone-width">
      <div class="title">Mortgage<br>Calculator</div>

      <div class="glass-card">
        <div class="input-grid">
          <div>
            <div class="field">
              <label for="loanAmount">Loan Amount</label>
              <input
                id="loanAmount"
                type="text"
                inputmode="numeric"
                value="${DEFAULT_LOAN_AMOUNT:,}"
              />
            </div>

            <div class="field">
              <label for="creditRange">Credit Score</label>
              <select id="creditRange">
                {option_tags(credit_ranges, selected=DEFAULT_CREDIT_RANGE)}
              </select>
            </div>
          </div>

          <div>
            <div class="field">
              <label for="loanType">Loan Type</label>
              <select id="loanType">
                {option_tags(loan_types, selected=DEFAULT_LOAN_TYPE)}
              </select>
            </div>

            <div class="field">
              <label for="loanTerm">Loan Term</label>
              <select id="loanTerm">
                {option_tags(term_years, selected=DEFAULT_LOAN_TERM, label_fn=lambda term: f"{term} years")}
              </select>
            </div>
          </div>
        </div>

        <div class="pill-row">
          <div class="pill-stack">
            <div class="pill-label">Down Payment</div>
            <div class="blue-pill" id="downPaymentDollars"></div>
          </div>
          <div class="white-pill" id="downPaymentPercent"></div>
        </div>

        <input
          id="downPaymentSlider"
          type="range"
          min="0"
          max="50"
          step="1"
          value="{DEFAULT_DOWN_PAYMENT_PCT}"
        />

        <div class="payment-card">
          <div class="payment-title">Estimated Monthly Payment</div>
          <div class="big-payment" id="monthlyPayment"></div>
          <div class="subtle">principal + interest</div>
        </div>
      </div>

      <div class="snap-hint">Swipe up for more info</div>
    </div>
  </section>

  <section class="snap-page">
    <div class="phone-width dummy-page">
      <h2>Contact Form</h2>
      <p>Dummy page.</p>
      <div class="snap-hint">Swipe down to go back ↓</div>
    </div>
  </section>

</div>

<script>
  const rateMap = {json.dumps(rate_map)};

  const streamlitScrollerSelectors = [
    "section.stAppViewMain",
    "section.main",
    "section[data-testid='stMain']",
    "div[data-testid='stAppViewContainer'] > section"
  ];

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

  function getParentDocument() {{
    try {{
      return window.parent.document;
    }} catch (error) {{
      return document;
    }}
  }}

  function parseCurrency(value) {{
    return Number(String(value).replace(/[^0-9]/g, "")) || 0;
  }}

  function formatCurrencyInput(value) {{
    const numericValue = parseCurrency(value);
    return numericValue ? currency.format(numericValue) : "";
  }}

  function calculateMonthlyPayment(principal, annualRate, years) {{
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
    const loanAmount = parseCurrency(loanAmountEl.value);
    const creditRange = creditRangeEl.value;
    const loanTerm = Number(loanTermEl.value);
    const downPaymentPct = Number(downPaymentSliderEl.value);

    const downPayment = loanAmount * downPaymentPct / 100;
    const principal = loanAmount - downPayment;
    const annualRate = rateMap[String(loanTerm)][creditRange];
    const payment = calculateMonthlyPayment(principal, annualRate, loanTerm);

    downPaymentDollarsEl.textContent = currency.format(downPayment);
    downPaymentPercentEl.textContent = `${{downPaymentPct}}%`;
    monthlyPaymentEl.textContent = currency.format(payment);
  }}

  function findStreamlitScroller() {{
    const doc = getParentDocument();

    return (
      streamlitScrollerSelectors
        .map((selector) => doc.querySelector(selector))
        .find(Boolean) ||
      doc.scrollingElement
    );
  }}

  function applyStreamlitSnapPatch() {{
    const doc = getParentDocument();

    streamlitScrollerSelectors.forEach((selector) => {{
      const el = doc.querySelector(selector);

      if (!el) {{
        return;
      }}

      Object.assign(el.style, {{
        height: "100svh",
        maxHeight: "100svh",
        overflowY: "auto",
        overflowX: "hidden",
        scrollSnapType: "y mandatory",
        scrollPadding: "0",
        webkitOverflowScrolling: "touch",
        overscrollBehaviorY: "contain"
      }});
    }});

    const block = doc.querySelector("[data-testid='stMainBlockContainer'], .block-container");

    if (block) {{
      Object.assign(block.style, {{
        padding: "0",
        margin: "0",
        maxWidth: "none",
        width: "100%"
      }});
    }}
  }}

  function snapToNearestPage() {{
    const scroller = findStreamlitScroller();
    const pages = Array.from(document.querySelectorAll(".snap-page"));

    if (!scroller || pages.length === 0) {{
      return;
    }}

    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const targetIndex = Math.max(
      0,
      Math.min(
        pages.length - 1,
        Math.round(scroller.scrollTop / viewportHeight)
      )
    );

    scroller.scrollTo({{
      top: targetIndex * viewportHeight,
      behavior: "smooth"
    }});
  }}

  let snapTimer = null;

  function installSnapFallback() {{
    const scroller = findStreamlitScroller();

    if (!scroller || scroller.__snapFallbackInstalled) {{
      return;
    }}

    scroller.__snapFallbackInstalled = true;

    scroller.addEventListener("scroll", () => {{
      window.clearTimeout(snapTimer);
      snapTimer = window.setTimeout(snapToNearestPage, 90);
    }}, {{ passive: true }});
  }}

  function refreshStreamlitLayout() {{
    applyStreamlitSnapPatch();
    installSnapFallback();
  }}

  loanAmountEl.addEventListener("input", () => {{
    loanAmountEl.value = loanAmountEl.value.replace(/[^0-9]/g, "");
    updateCalculator();
  }});

  loanAmountEl.addEventListener("focus", () => {{
    const numericValue = parseCurrency(loanAmountEl.value);
    loanAmountEl.value = numericValue ? String(numericValue) : "";
  }});

  loanAmountEl.addEventListener("blur", () => {{
    loanAmountEl.value = formatCurrencyInput(loanAmountEl.value);
    updateCalculator();
  }});

  loanAmountEl.addEventListener("keydown", (event) => {{
    if (event.key === "Escape" || event.key === "Enter") {{
      loanAmountEl.blur();
    }}
  }});

  [creditRangeEl, loanTermEl, downPaymentSliderEl].forEach((element) => {{
    element.addEventListener("input", updateCalculator);
    element.addEventListener("change", updateCalculator);
  }});

  updateCalculator();
  refreshStreamlitLayout();

  [250, 1000].forEach((delay) => {{
    window.setTimeout(refreshStreamlitLayout, delay);
  }});

  window.addEventListener("resize", refreshStreamlitLayout);
</script>
"""

st.html(html, unsafe_allow_javascript=True)



# TODO:
#   slider:
#     make knob larger
#     knob style is different between desktop and ios
#     remove slider track border
#   background gradient should be for view size not entire length
#   - when trying to scroll past first / last pages, two layers of gradients show with a hard edge
#   scroll bar does not appear on desktop
#   scrolling on ios still doesn't hide the toolbar
#   tap the down payment dollar & percent labels to manually enter a value
#   dollar & percent labels are not the same height
#   dollar label title needs bottom margin
