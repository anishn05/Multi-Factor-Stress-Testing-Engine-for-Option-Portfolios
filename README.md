# Multi-Factor Stress Testing Engine for Option Portfolios

A **scenario-based stress testing engine** for equity option portfolios. Build portfolios, apply multi-factor stress scenarios, visualize PnL attribution, and validate the risk model—all through an interactive **Streamlit dashboard**.

---

## 📸 Screenshots

### Dashboard Overview
(images/EquitySellOff_1.png)
(images/EquitySellOff_2.png)

## Features

### Portfolio Management
- Build equity option portfolios from scratch or **load preset ATM straddles**.
- Add individual options with:
  - Option type (Call / Put)  
  - Strike  
  - Quantity  
  - Maturity (in days)  

### Scenario Stress Engine
- Apply **pre-defined scenario categories**:
  - Apply spot shocks
  - Parallel volatility shifts  
  - Skew adjustments  
  - Convexity / curvature changes  
- Real-time updates with portfolio changes.

### PnL & Risk Analytics
- Compute **base value**, **stressed value**, and **PnL impact**.
- **PnL Attribution** by Greeks: delta, gamma, vega, theta, residual.
- **Model validity diagnostics**:
  - Spot move percentage  
  - Gamma ratio  
  - Residual ratio  
  - Greeks reliability flag  
- Convexity & residual error visualization.

### Visualizations
- **2x2 plots** per scenario:
  1. Spot shock visualization  
  2. PnL attribution by Greeks  
  3. Explained PnL vs full revaluation + error bands  
  4. Model validity & convexity flags  

### Dashboard Features
- Built with **Streamlit**.
- Sidebar inputs for scenario selection, portfolio construction, clearing, and running scenarios.

### Market Data Integration
- Loads real **option chains** via Yahoo Finance (`yfinance`).
- Fetches **spot price data** for underlying equities.
- Builds **implied volatility surfaces** for portfolio pricing.
- Prices portfolios using **Black-Scholes-based PortfolioPricer**.