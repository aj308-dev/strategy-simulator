import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Business Strategy Simulator", page_icon="📊", layout="wide")

# --- Page Navigation ---
pages = ["Welcome", "Inputs", "Simulation", "Insights & Feedback", "Export"]
page = st.sidebar.radio("📂 Navigation", pages)

# --- Shared state ---
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = None
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}

# --- PAGE 1: Welcome ---
if page == "Welcome":
    st.title("📊 Business Strategy Simulator")
    st.markdown("""
    ### Plan, simulate, and improve your business strategies  
    This tool lets you:
    - Enter your business metrics
    - Simulate performance month-by-month
    - Get automatic feedback & improvement tips
    - Export results as CSV or PDF

    **Start by going to the _Inputs_ page in the left menu.**
    """)
    st.image("https://images.unsplash.com/photo-1542744173-8e7e53415bb0", use_column_width=True)

# --- PAGE 2: Inputs ---
elif page == "Inputs":
    st.title("📥 Enter Your Business Metrics")

    mrr = st.number_input("💰 Monthly Recurring Revenue (MRR) [$]", min_value=0.0, value=10000.0, step=100.0,
                          help="The revenue you earn every month from subscriptions or contracts.")
    customers = st.number_input("👥 Current Customers", min_value=0, value=100, step=1,
                                 help="Number of paying customers right now.")
    churn_rate = st.number_input("📉 Monthly Churn Rate (%)", min_value=0.0, value=5.0, step=0.1,
                                  help="The % of customers who leave each month.")
    cac = st.number_input("🎯 Customer Acquisition Cost (CAC) [$]", min_value=0.0, value=200.0, step=10.0,
                           help="Average cost to acquire one new customer.")
    marketing_budget = st.number_input("📢 Monthly Marketing Budget [$]", min_value=0.0, value=5000.0, step=100.0,
                                       help="Amount you spend monthly to acquire customers.")
    arpu = st.number_input("💵 Average Revenue Per User (ARPU) [$]", min_value=0.0, value=100.0, step=1.0,
                           help="Average monthly revenue per customer.")
    months = st.slider("🗓 Simulation Duration (months)", min_value=1, max_value=36, value=12)

    if st.button("Run Simulation"):
        st.session_state.inputs = {
            "mrr": mrr,
            "customers": customers,
            "churn_rate": churn_rate / 100,
            "cac": cac,
            "marketing_budget": marketing_budget,
            "arpu": arpu,
            "months": months
        }

        # Run simulation
        data = []
        curr_customers = customers
        curr_mrr = mrr
        for month in range(1, months + 1):
            churned = curr_customers * st.session_state.inputs["churn_rate"]
            new_customers = marketing_budget / cac if cac > 0 else 0
            curr_customers = curr_customers - churned + new_customers
            curr_mrr = curr_customers * arpu
            data.append({
                "Month": month,
                "Customers": round(curr_customers, 2),
                "MRR": round(curr_mrr, 2),
                "New Customers": round(new_customers, 2),
                "Churned Customers": round(churned, 2)
            })

        st.session_state.simulation_data = pd.DataFrame(data)
        st.success("Simulation completed! Go to the **Simulation** page to see results.")

# --- PAGE 3: Simulation ---
elif page == "Simulation":
    st.title("📈 Simulation Results")
    if st.session_state.simulation_data is not None:
        st.dataframe(st.session_state.simulation_data)

        fig1 = px.line(st.session_state.simulation_data, x="Month", y="Customers", title="Customer Growth Over Time")
        fig2 = px.line(st.session_state.simulation_data, x="Month", y="MRR", title="MRR Growth Over Time")

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Please run a simulation from the **Inputs** page first.")

# --- PAGE 4: Insights ---
elif page == "Insights & Feedback":
    st.title("💡 Insights & Feedback")
    if st.session_state.simulation_data is not None:
        df = st.session_state.simulation_data
        final_customers = df["Customers"].iloc[-1]
        final_mrr = df["MRR"].iloc[-1]
        churn_rate = st.session_state.inputs["churn_rate"]
        cac = st.session_state.inputs["cac"]
        arpu = st.session_state.inputs["arpu"]

        ltv = arpu * (1 / churn_rate) if churn_rate > 0 else float('inf')
        ltv_cac = ltv / cac if cac > 0 else float('inf')

        st.metric("Final Customers", round(final_customers))
        st.metric("Final MRR ($)", round(final_mrr))
        st.metric("LTV ($)", round(ltv, 2))
        st.metric("LTV : CAC", round(ltv_cac, 2))

        if churn_rate > 0.07:
            st.error("⚠ High churn rate — aim for below 7% per month.")
        elif churn_rate > 0.05:
            st.warning("⚠ Churn slightly high — aim for below 5% per month.")
        else:
            st.success("✅ Healthy churn rate!")

        if ltv_cac < 3:
            st.error("⚠ LTV:CAC ratio too low — aim for at least 3:1.")
        else:
            st.success("✅ Good LTV:CAC ratio.")
    else:
        st.warning("Please run a simulation first.")

# --- PAGE 5: Export ---
elif page == "Export":
    st.title("📤 Export Results")
    if st.session_state.simulation_data is not None:
        csv = st.session_state.simulation_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download as CSV", data=csv, file_name='simulation_results.csv', mime='text/csv')
    else:
        st.warning("Please run a simulation first.")
