import json
import streamlit as st

from utils import term_years, annual_rate


st.set_page_config(
    page_title="Mortgage Calculator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp {
        overflow: hidden;
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
      }

      .block-container {
        padding: 0 !important;
        max-width: none !important;
      }

      header,
      footer,
      [data-testid="stToolbar"],
      [data-testid="stDecoration"] {
        display: none !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
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
<style>
  * {{
    box-sizing: border-box;
  }}

  html,
  body {{
    margin: 0;
    overflow: hidden;
    overscroll-behavior: none;
  }}

  .page-shell {{
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100dvh;
    overflow: hidden;
    cursor: grab;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
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

  .page-shell.is-dragging {{
    cursor: grabbing;
  }}

  .page-track {{
    width: 100%;
    height: 100%;
    transform: translate3d(0, 0, 0);
    transition: transform 560ms cubic-bezier(.22, 1, .36, 1);
    will-change: transform;
  }}

  .page-track.is-dragging {{
    transition: none;
  }}

  .snap-page {{
    width: 100%;
    height: 100dvh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: max(1rem, env(safe-area-inset-top)) 1rem max(1rem, env(safe-area-inset-bottom));
  }}

  .phone-width {{
    width: 100%;
    max-width: 430px;
  }}

  input,
  textarea {{
    user-select: text;
    -webkit-user-select: text;
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
    user-select: auto;
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

  .dummy-page {{
    color: white;
    text-align: center;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Inter, sans-serif;
  }}

  .dummy-page h2 {{
    font-size: 2.25rem;
    margin: 0 0 0.75rem;
  }}

  .dummy-page p {{
    margin: 0;
    color: rgba(255,255,255,.78);
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

<div class="page-shell" id="pageShell">
  <main class="page-track" id="pageTrack">
    <section class="snap-page">
      <div class="phone-width">
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
                  {"".join(f'<option value="{credit}">{credit}</option>' for credit in credit_ranges)}
                </select>
              </div>
            </div>

            <div>
              <div class="field">
                <label for="loanType">Loan Type</label>
                <select id="loanType">
                  {"".join(f'<option value="{loan_type}">{loan_type}</option>' for loan_type in loan_types)}
                </select>
              </div>

              <div class="field">
                <label for="loanTerm">Loan Term</label>
                <select id="loanTerm">
                  {"".join(f'<option value="{term}" {"selected" if term == 30 else ""}>{term} years</option>' for term in term_years)}
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

        <div class="snap-hint">Swipe up for details ↑</div>
      </div>
    </section>

    <section class="snap-page">
      <div class="phone-width dummy-page">
        <h2>Payment Details</h2>
        <p>Dummy second page for snap scrolling.</p>
      </div>
    </section>
  </main>
</div>

<script>
  const rateMap = {json.dumps(rate_map)};
  const pageShell = document.getElementById("pageShell");
  const pageTrack = document.getElementById("pageTrack");
  const pages = Array.from(document.querySelectorAll(".snap-page"));

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

  let currentPage = 0;
  let currentTranslateY = 0;
  let isAnimating = false;
  let isDragging = false;
  let animationTimer = null;
  let pointerId = null;
  let dragStartY = 0;
  let dragStartTranslateY = 0;
  let lastPointerY = 0;
  let lastPointerTime = 0;
  let dragVelocityY = 0;

  function getViewportHeight() {{
    return window.innerHeight || document.documentElement.clientHeight;
  }}

  function clamp(value, min, max) {{
    return Math.max(min, Math.min(value, max));
  }}

  function getPageTranslateY(pageIndex) {{
    return -pageIndex * getViewportHeight();
  }}

  function getCurrentRenderedTranslateY() {{
    const transform = window.getComputedStyle(pageTrack).transform;

    if (!transform || transform === "none") {{
      return currentTranslateY;
    }}

    return new DOMMatrixReadOnly(transform).m42;
  }}

  function setTrackTranslateY(translateY) {{
    currentTranslateY = translateY;
    pageTrack.style.transform = `translate3d(0, ${{translateY}}px, 0)`;
  }}

  function setDraggingState(enabled) {{
    isDragging = enabled;
    pageShell.classList.toggle("is-dragging", enabled);
    pageTrack.classList.toggle("is-dragging", enabled);
  }}

  function stopAnimationAtCurrentPosition() {{
    if (animationTimer !== null) {{
      window.clearTimeout(animationTimer);
      animationTimer = null;
    }}

    const renderedTranslateY = getCurrentRenderedTranslateY();

    isAnimating = false;
    setDraggingState(true);
    setTrackTranslateY(renderedTranslateY);

    pageTrack.getBoundingClientRect();
  }}

  function getNearestPageFromTranslateY(translateY) {{
    const pageIndex = Math.round(-translateY / getViewportHeight());
    return clamp(pageIndex, 0, pages.length - 1);
  }}

  function dampenBoundaryTranslateY(translateY) {{
    const maxTranslateY = 0;
    const minTranslateY = getPageTranslateY(pages.length - 1);

    if (translateY > maxTranslateY) {{
      return maxTranslateY + (translateY - maxTranslateY) * 0.28;
    }}

    if (translateY < minTranslateY) {{
      return minTranslateY + (translateY - minTranslateY) * 0.28;
    }}

    return translateY;
  }}

  function goToPage(nextPage) {{
    const clampedPage = clamp(nextPage, 0, pages.length - 1);
    const targetTranslateY = getPageTranslateY(clampedPage);

    if (!isDragging && Math.abs(currentTranslateY - targetTranslateY) < 0.5) {{
      currentPage = clampedPage;
      return;
    }}

    if (animationTimer !== null) {{
      window.clearTimeout(animationTimer);
      animationTimer = null;
    }}

    currentPage = clampedPage;
    isAnimating = true;
    setDraggingState(false);
    setTrackTranslateY(targetTranslateY);

    animationTimer = window.setTimeout(() => {{
      isAnimating = false;
      animationTimer = null;
      currentTranslateY = targetTranslateY;
    }}, 620);
  }}

  function isTextInputElement(element) {{
    return element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement;
  }}

  function isInteractiveElement(target) {{
    return Boolean(target.closest("input, select, textarea, button, label"));
  }}

  function hasSelectedInputText() {{
    const activeElement = document.activeElement;

    if (!isTextInputElement(activeElement)) {{
      return false;
    }}

    return activeElement.selectionStart !== activeElement.selectionEnd;
  }}

  function hasDocumentSelection() {{
    const selection = window.getSelection();

    return Boolean(selection && !selection.isCollapsed && selection.toString().length > 0);
  }}

  function hasActiveTextSelection() {{
    return hasSelectedInputText() || hasDocumentSelection();
  }}

  function clearTextSelection() {{
    const activeElement = document.activeElement;

    if (isTextInputElement(activeElement)) {{
      const caretPosition = activeElement.selectionEnd || activeElement.value.length;
      activeElement.setSelectionRange(caretPosition, caretPosition);
      activeElement.blur();
    }}

    const selection = window.getSelection();

    if (selection) {{
      selection.removeAllRanges();
    }}
  }}

  function shouldClearSelectionBeforeDrag(target) {{
    return hasActiveTextSelection() && !isInteractiveElement(target);
  }}

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

  function handleWheel(event) {{
    if (isInteractiveElement(event.target) || hasActiveTextSelection()) {{
      return;
    }}

    event.preventDefault();

    if (isDragging || Math.abs(event.deltaY) < 8) {{
      return;
    }}

    if (isAnimating) {{
      stopAnimationAtCurrentPosition();
      setDraggingState(false);
    }}

    currentPage = getNearestPageFromTranslateY(currentTranslateY);
    goToPage(currentPage + Math.sign(event.deltaY));
  }}

  function handlePointerDown(event) {{
    if (pointerId !== null) {{
      return;
    }}

    if (shouldClearSelectionBeforeDrag(event.target)) {{
      event.preventDefault();
      clearTextSelection();
      return;
    }}

    if (isInteractiveElement(event.target) || hasActiveTextSelection()) {{
      return;
    }}

    event.preventDefault();

    if (isAnimating) {{
      stopAnimationAtCurrentPosition();
    }} else {{
      setDraggingState(true);
      setTrackTranslateY(getCurrentRenderedTranslateY());
    }}

    pointerId = event.pointerId;
    dragStartY = event.clientY;
    dragStartTranslateY = currentTranslateY;
    lastPointerY = event.clientY;
    lastPointerTime = performance.now();
    dragVelocityY = 0;

    pageShell.setPointerCapture(pointerId);
  }}

  function handlePointerMove(event) {{
    if (!isDragging || event.pointerId !== pointerId) {{
      return;
    }}

    event.preventDefault();

    const now = performance.now();
    const elapsed = Math.max(1, now - lastPointerTime);
    const pointerDeltaY = event.clientY - lastPointerY;

    dragVelocityY = pointerDeltaY / elapsed;
    lastPointerY = event.clientY;
    lastPointerTime = now;

    const rawTranslateY = dragStartTranslateY + event.clientY - dragStartY;
    setTrackTranslateY(dampenBoundaryTranslateY(rawTranslateY));
  }}

  function handlePointerUp(event) {{
    if (!isDragging || event.pointerId !== pointerId) {{
      return;
    }}

    const viewportHeight = getViewportHeight();
    const distanceThreshold = Math.min(140, viewportHeight * 0.18);
    const velocityThreshold = 0.55;
    const dragDistance = currentTranslateY - dragStartTranslateY;
    const startPage = getNearestPageFromTranslateY(dragStartTranslateY);

    let targetPage = getNearestPageFromTranslateY(currentTranslateY);

    if (Math.abs(dragVelocityY) > velocityThreshold) {{
      targetPage = startPage + (dragVelocityY < 0 ? 1 : -1);
    }} else if (Math.abs(dragDistance) > distanceThreshold) {{
      targetPage = startPage + (dragDistance < 0 ? 1 : -1);
    }} else {{
      targetPage = startPage;
    }}

    if (pageShell.hasPointerCapture(pointerId)) {{
      pageShell.releasePointerCapture(pointerId);
    }}

    pointerId = null;
    goToPage(targetPage);
  }}

  function handlePointerCancel(event) {{
    if (!isDragging || event.pointerId !== pointerId) {{
      return;
    }}

    if (pageShell.hasPointerCapture(pointerId)) {{
      pageShell.releasePointerCapture(pointerId);
    }}

    pointerId = null;
    goToPage(getNearestPageFromTranslateY(currentTranslateY));
  }}

  [
    loanAmountEl,
    creditRangeEl,
    loanTermEl,
    downPaymentSliderEl
  ].forEach((element) => {{
    element.addEventListener("input", updateCalculator);
    element.addEventListener("change", updateCalculator);
  }});

  window.addEventListener("wheel", handleWheel, {{ passive: false }});
  pageShell.addEventListener("pointerdown", handlePointerDown);
  pageShell.addEventListener("pointermove", handlePointerMove);
  pageShell.addEventListener("pointerup", handlePointerUp);
  pageShell.addEventListener("pointercancel", handlePointerCancel);
  window.addEventListener("resize", () => goToPage(getNearestPageFromTranslateY(currentTranslateY)));

  updateCalculator();
  setTrackTranslateY(getPageTranslateY(currentPage));
</script>
"""

st.html(html, unsafe_allow_javascript=True)



# TODO:
#     bug where we can accidentally highlight text while dragging the page.
#     drag / release cursor bugged on firefox (in iphone emulation mode)
