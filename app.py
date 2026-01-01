# app.py
import streamlit as st
from engine.scenarios import SCENARIOS
from engine.main_engine import run_scenario
from engine.build_context import build_context
from market_data.option_chain import OptionChainLoader
from instruments.option import EuropeanOption
from instruments.portfolio import OptionPortfolio

# ----------------------------
# Streamlit page setup
# ----------------------------
st.set_page_config(
    page_title="Stress Testing & PnL Explain",
    layout="wide"
)

st.title("📊 Portfolio Stress Testing & PnL Attribution")
st.caption("SPY Equity Options | Scenario-Based Stress Engine")

# ----------------------------
# Load context (spot, surface, pricer, etc.)
# ----------------------------
@st.cache_resource
def load_context():
    return build_context()

context = load_context()
loader = context["chain_loader"]

# ----------------------------
# Sidebar: Scenario Selection
# ----------------------------
scenario_name = st.sidebar.selectbox(
    "Select Scenario", list(SCENARIOS.keys())
)

# ----------------------------
# Sidebar: Portfolio Builder
# ----------------------------
st.sidebar.header("📦 Portfolio Builder")

# Option inputs
option_type = st.sidebar.selectbox("Option Type", ["Call", "Put"])
strike = st.sidebar.number_input("Strike", value=100.0)
quantity = st.sidebar.number_input("Quantity", value=1, step=1)
maturity_days = st.sidebar.number_input("Days to Maturity", value=30)

# Initialize session state for portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = OptionPortfolio()

# Add a manual option
if st.sidebar.button("Add Option"):
    maturity = maturity_days / 365.0
    st.session_state.portfolio.add(
        EuropeanOption(
            strike=strike,
            maturity=maturity,
            option_type=option_type,
            quantity=quantity
        )
    )

# Load preset ATM straddle
if st.sidebar.button("Load ATM Straddle (Preset)"):
    expiry = loader.get_expirations()[10]
    spot = context["surface"].spot
    maturity = maturity_days / 365.0  # use dashboard-selected maturity
    st.session_state.portfolio = loader.build_portfolio(
        expiry=expiry,
        spot=spot,
        base_size=10,
        maturity=maturity
    )

# Clear portfolio
if st.sidebar.button("Clear Portfolio"):
    st.session_state.portfolio = OptionPortfolio()

# ----------------------------
# Show portfolio holdings
# ----------------------------
st.subheader("📦 Portfolio Holdings")
if len(st.session_state.portfolio) == 0:
    st.info("Portfolio is empty.")
else:
    st.table([
        {
            "Type": opt.option_type,
            "Strike": opt.strike,
            "Maturity (yrs)": round(opt.maturity, 3),
            "Quantity": opt.quantity,
        }
        for opt in st.session_state.portfolio
    ])

# ----------------------------
# Run Scenario Button
# ----------------------------
if st.sidebar.button("Run Scenario"):
    result = run_scenario(
        context=context,
        scenario=SCENARIOS[scenario_name],
        portfolio=st.session_state.portfolio
    )

    # ----------------------------
    # Headline Metrics
    # ----------------------------
    st.subheader(f"Scenario: {scenario_name}")
    scenario_desc = SCENARIOS[scenario_name].get("description", "")
    if scenario_desc:
        st.caption(scenario_desc)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Base Value", f"{result['base_value']:,.2f}")
    col2.metric("Stressed Value", f"{result['stressed_value']:,.2f}")
    col3.metric("PnL Impact", f"{result['pnl']:,.2f}", delta=f"{result['pnl']:,.2f}")

    # ----------------------------
    # PnL Attribution
    # ----------------------------
    st.subheader("PnL Attribution")
    st.table({
        "Component": list(result["pnl_breakdown"].keys()),
        "PnL": [f"{v:,.2f}" for v in result["pnl_breakdown"].values()]
    })

    # ----------------------------
    # Model Validity Diagnostics
    # ----------------------------
    st.subheader("Model Validity Diagnostics")
    diag = result["diagnostics"]
    diag_cols = st.columns(4)
    diag_cols[0].metric("Spot Move %", f"{diag['spot_move_pct']*100:.2f}%")
    diag_cols[1].metric("Residual Ratio", f"{diag['residual_ratio']:.4f}")
    diag_cols[2].metric("Gamma Ratio", f"{diag['gamma_ratio']:.4f}")
    diag_cols[3].metric("Greeks Trustworthy", "Yes" if diag["greeks_trustworthy"] else "No")

    if not diag["greeks_trustworthy"]:
        st.warning("⚠ Greeks outside validity regime — PnL explain may be unreliable.")

    # ----------------------------
    # Stress & Attribution Plots
    # ----------------------------
    st.subheader("Stress & Attribution Visuals")
    fig = result["plots"]  # your 2x2 matplotlib/seaborn figure
    st.pyplot(fig)
