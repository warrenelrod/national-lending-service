import streamlit as st

st.set_page_config(
    page_title="Mortgage Calculator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

import streamlit.components.v1 as components

components.html(
    """
    <script>
    (function () {
        const parentWindow = window.parent;
        const parentDoc = parentWindow.document;

        let lastVisualHeight = null;
        let lastInnerHeight = null;
        let logCount = 0;

        function getViewportSnapshot() {
            const vv = parentWindow.visualViewport;

            return {
                visualHeight: vv ? Math.round(vv.height) : Math.round(parentWindow.innerHeight),
                visualWidth: vv ? Math.round(vv.width) : Math.round(parentWindow.innerWidth),
                innerHeight: Math.round(parentWindow.innerHeight),
                innerWidth: Math.round(parentWindow.innerWidth),
                offsetTop: vv ? Math.round(vv.offsetTop) : 0,
                offsetLeft: vv ? Math.round(vv.offsetLeft) : 0,
                scale: vv ? vv.scale : 1,
                screenHeight: parentWindow.screen ? parentWindow.screen.height : null,
            };
        }

        function writeToViewportConsole(payload) {
            const output = parentDoc.getElementById("viewport-console-output");

            if (!output) {
                return;
            }

            output.textContent =
                JSON.stringify(payload, null, 2) +
                "\\n\\n" +
                output.textContent;
        }

        function pushViewportLog(message, snapshot) {
            logCount += 1;

            const payload = {
                count: logCount,
                time: new Date().toLocaleTimeString(),
                message,
                ...snapshot,
            };

            console.log("[viewport]", payload);
            writeToViewportConsole(payload);
        }

        function checkViewport(reason) {
            const snapshot = getViewportSnapshot();

            if (lastVisualHeight === null) {
                lastVisualHeight = snapshot.visualHeight;
                lastInnerHeight = snapshot.innerHeight;

                pushViewportLog("Initial viewport measurement", {
                    reason,
                    ...snapshot,
                    visualHeightDelta: 0,
                    innerHeightDelta: 0,
                });

                return;
            }

            const visualHeightDelta = snapshot.visualHeight - lastVisualHeight;
            const innerHeightDelta = snapshot.innerHeight - lastInnerHeight;

            const changed = visualHeightDelta !== 0 || innerHeightDelta !== 0;

            if (changed) {
                pushViewportLog(
                    visualHeightDelta > 0 || innerHeightDelta > 0
                        ? "More screen space available"
                        : "Less screen space available",
                    {
                        reason,
                        ...snapshot,
                        previousVisualHeight: lastVisualHeight,
                        previousInnerHeight: lastInnerHeight,
                        visualHeightDelta,
                        innerHeightDelta,
                    }
                );

                lastVisualHeight = snapshot.visualHeight;
                lastInnerHeight = snapshot.innerHeight;
            }
        }

        checkViewport("script loaded");

        if (parentWindow.visualViewport) {
            parentWindow.visualViewport.addEventListener("resize", function () {
                checkViewport("parent visualViewport resize");
            });

            parentWindow.visualViewport.addEventListener("scroll", function () {
                checkViewport("parent visualViewport scroll");
            });
        }

        parentWindow.addEventListener("resize", function () {
            checkViewport("parent window resize");
        });

        parentWindow.addEventListener("orientationchange", function () {
            setTimeout(function () {
                checkViewport("orientationchange");
            }, 300);
        });

        // Fallback for mobile browsers that do not reliably fire visualViewport events
        setInterval(function () {
            checkViewport("poll");
        }, 250);

        // When the last-page debug element appears later, write the latest state into it
        const observer = new MutationObserver(function () {
            const output = parentDoc.getElementById("viewport-console-output");

            if (output && output.textContent.includes("Waiting for viewport changes")) {
                const snapshot = getViewportSnapshot();
                pushViewportLog("Debug console connected", {
                    reason: "mutation observer",
                    ...snapshot,
                    visualHeightDelta: 0,
                    innerHeightDelta: 0,
                });
            }
        });

        observer.observe(parentDoc.body, {
            childList: true,
            subtree: true,
        });
    })();
    </script>
    """,
    height=0,
)

st.markdown(
    """
    <style>
    html,
    body {
        height: 100%;
        overflow: hidden;
        overscroll-behavior: none;
    }

    .stApp {
        height: 100dvh;
        overflow: hidden;
        background:
            radial-gradient(
                circle at 95% 6%,
                rgba(150, 135, 255, 0.55) 0%,
                rgba(115, 95, 235, 0.38) 28%,
                rgba(70, 50, 170, 0.18) 52%,
                rgba(11, 8, 40, 0) 78%
            ),
            linear-gradient(
                180deg,
                #1b0f68 0%,
                #24147f 34%,
                #171052 58%,
                #07051f 100%
            );
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
    }

    section.main,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stMain"],
    div[data-testid="stMainBlockContainer"] {
        height: 100dvh;
    }

    .block-container {
        max-width: 430px;
        height: 100dvh;
        overflow-y: scroll;
        overflow-x: hidden;

        scroll-snap-type: y mandatory;
        scroll-padding: 0;
        scroll-behavior: auto;

        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;

        -webkit-overflow-scrolling: auto;
        overscroll-behavior-y: contain;
    }

    .block-container::-webkit-scrollbar {
        display: none;
    }

    .st-key-input_section,
    .st-key-result_section,
    .st-key-breakdown_section {
        height: 100dvh;
        min-height: 100dvh;
        max-height: 100dvh;

        scroll-snap-align: start;
        scroll-snap-stop: always;

        display: flex;
        flex-direction: column;
        justify-content: center;

        padding: 1.25rem 0;
        box-sizing: border-box;
    }

    .viewport-debug-card {
        background: rgba(0, 0, 0, 0.72);
        color: #d8ffdf;
        border-radius: 18px;
        padding: 1rem;
        margin-top: 0.85rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        box-shadow: 0 14px 34px rgba(0,0,0,0.18);
    }

    .viewport-debug-title {
        color: white;
        font-size: 0.9rem;
        font-weight: 850;
        margin-bottom: 0.6rem;
    }

    #viewport-console-output {
        white-space: pre-wrap;
        font-size: 0.72rem;
        line-height: 1.35;
        max-height: 160px;
        overflow-y: auto;
    }

    header, footer {
        visibility: hidden;
    }

    h1 {
        color: white;
        font-size: 3.15rem !important;
        line-height: 0.95 !important;
        letter-spacing: -0.08em;
        font-weight: 850 !important;
        margin-bottom: 1.2rem !important;
    }

    .st-key-glass_card {
        background: rgba(255, 255, 255, 0.74);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 22px;
        padding: 1.25rem 1.1rem 1.45rem 1.1rem;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.45),
            0 18px 45px rgba(25,25,110,0.20);
    }

    .payment-card {
        background: rgba(255,255,255,0.9);
        border-radius: 24px;
        padding: 1.35rem 1.15rem;
        box-shadow: 0 14px 34px rgba(0,0,0,0.08);
    }

    label, .stSlider label, .stSelectbox label, .stNumberInput label {
        color: #151515 !important;
        font-size: 0.95rem !important;
        font-weight: 750 !important;
    }

    .stNumberInput input {
        background: rgba(255,255,255,0.84) !important;
        border: none !important;
        border-radius: 11px !important;
        font-size: 1.15rem !important;
        font-weight: 750 !important;
        color: #111 !important;
    }

    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.84) !important;
        border: none !important;
        border-radius: 11px !important;
        font-size: 1rem !important;
        font-weight: 750 !important;
        color: #111 !important;
    }

    .stSlider [role="slider"] {
        background-color: #4156f4 !important;
        border: 3px solid white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,.25);
    }

    .stSlider [data-testid="stThumbValue"] {
        background: #4156f4 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
    }

    .pill-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -0.25rem;
    }

    .blue-pill {
        background: #4156f4;
        color: white;
        font-size: 1.25rem;
        font-weight: 850;
        padding: 0.45rem 0.7rem;
        border-radius: 11px;
        box-shadow: 0 3px 8px rgba(65,86,244,.32);
    }

    .white-pill {
        background: white;
        color: #111;
        font-size: 1.15rem;
        font-weight: 850;
        padding: 0.45rem 0.7rem;
        border-radius: 11px;
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
        margin-bottom: 1.15rem;
    }

    .total {
        color: #333;
        font-size: 0.98rem;
        line-height: 1.3;
    }

    .total strong {
        color: #111;
        font-weight: 850;
    }

    .snap-hint {
        text-align: center;
        color: rgba(255,255,255,.82);
        font-size: 0.82rem;
        margin-top: 1rem;
    }

    .dark-hint {
        text-align: center;
        color: rgba(255,255,255,.72);
        font-size: 0.82rem;
        margin-top: 1rem;
    }

    .metric-box {
        background: rgba(255,255,255,0.86);
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .metric-label {
        color: #555;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .metric-value {
        color: #111;
        font-size: 1.7rem;
        font-weight: 850;
        letter-spacing: -0.04em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 100 / 12
    months = years * 12

    if monthly_rate == 0:
        return principal / months

    return principal * (monthly_rate * (1 + monthly_rate) ** months) / (
        (1 + monthly_rate) ** months - 1
    )


if "loan_amount" not in st.session_state:
    st.session_state.loan_amount = 425_000

if "interest_rate" not in st.session_state:
    st.session_state.interest_rate = 6.875

if "loan_term" not in st.session_state:
    st.session_state.loan_term = 30

if "down_payment_pct" not in st.session_state:
    st.session_state.down_payment_pct = 20

if "taxes_insurance" not in st.session_state:
    st.session_state.taxes_insurance = 680


with st.container(key="input_section"):
    st.markdown(
        """
        <div style="padding-left: 0.6rem; padding-bottom: 0.5rem;">
            <span style="
                font-family: Arial, Helvetica, sans-serif;
                letter-spacing: 1px;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 44px;
                line-height: 1.1;
            ">
                Mortgage<br>Calculator
            </span>
        </div>
        """,
            unsafe_allow_html=True
        )

    # st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    with st.container(key="glass_card"):
        col1, col2 = st.columns(2)

        with col1:
            loan_amount = st.number_input(
                "Loan Amount",
                min_value=50_000,
                max_value=3_000_000,
                value=st.session_state.loan_amount,
                step=5_000,
                format="%d",
                key="loan_amount_widget",
            )

            interest_rate = st.selectbox(
                "Interest Rate",
                options=[4.875, 5.125, 5.500, 5.875, 6.125, 6.500, 6.875, 7.125, 7.500],
                index=[4.875, 5.125, 5.500, 5.875, 6.125, 6.500, 6.875, 7.125, 7.500].index(
                    st.session_state.interest_rate
                ),
                format_func=lambda x: f"{x:.3f}%",
                key="interest_rate_widget",
            )

        with col2:
            loan_term = st.selectbox(
                "Loan Term",
                options=[10, 15, 20, 25, 30],
                index=[10, 15, 20, 25, 30].index(st.session_state.loan_term),
                format_func=lambda x: f"{x} years",
                key="loan_term_widget",
            )

        down_payment_pct = st.slider(
            "Down Payment",
            min_value=0,
            max_value=50,
            value=st.session_state.down_payment_pct,
            step=1,
            format="%d%%",
            key="down_payment_widget",
        )

        down_payment = loan_amount * down_payment_pct / 100
        principal = loan_amount - down_payment

        st.markdown(
            f"""
            <div class="pill-row">
                <div class="blue-pill">${down_payment:,.0f}</div>
                <div class="white-pill">{down_payment_pct}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="snap-hint">Swipe up for payment ↑</div>', unsafe_allow_html=True)


principal_interest = monthly_payment(principal, interest_rate, loan_term)


with st.container(key="result_section"):
    st.markdown(
        f"""
        <div class="payment-card">
            <div class="payment-title">Estimated Monthly Payment</div>
            <div class="big-payment">${principal_interest:,.0f}</div>
            <div class="subtle">principal + interest</div>
        """,
        unsafe_allow_html=True,
    )

    taxes_insurance = st.slider(
        "Estimated taxes & insurance",
        min_value=0,
        max_value=2_000,
        value=st.session_state.taxes_insurance,
        step=25,
        format="$%d",
        key="taxes_insurance_widget",
    )

    total_monthly = principal_interest + taxes_insurance

    st.markdown(
        f"""
            <div class="total">
                Total monthly <strong>~${total_monthly:,.0f}</strong><br>
                including taxes &amp; insurance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dark-hint">Swipe up for breakdown ↑</div>', unsafe_allow_html=True)


with st.container(key="breakdown_section"):
    total_interest = principal_interest * loan_term * 12 - principal
    total_paid = principal + total_interest

    st.markdown(
        f"""
        <div class="payment-card">
            <div class="payment-title">Loan Breakdown</div>

            <div class="metric-box">
                <div class="metric-label">Loan Principal</div>
                <div class="metric-value">${principal:,.0f}</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Down Payment</div>
                <div class="metric-value">${down_payment:,.0f}</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Total Interest</div>
                <div class="metric-value">${total_interest:,.0f}</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Total Principal + Interest</div>
                <div class="metric-value">${total_paid:,.0f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="viewport-debug-card">
            <div class="viewport-debug-title">Viewport console</div>
            <pre id="viewport-console-output">Waiting for viewport changes...</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="dark-hint">Swipe down to go back ↓</div>', unsafe_allow_html=True)