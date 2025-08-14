import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Business Strategy Simulator", page_icon="📊", layout="wide")

# --- Helper functions ---
def download_link(df, file_type="csv"):
    buffer = BytesIO()
    if file_type == "csv":
        df.to_csv(buffer, index=False)
        mime = "text/csv"
        ext = "csv"
    elif file_type == "excel":
        df.to_excel(buffer, index=False)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="strategy_results.{ext}">📥 Download {file_type.upper()}</a>'
    return href

def generate_feedback(predicted, actual):
    gap = actual - predicted
    if gap > 0:
        return [
            "Your strategy performed better than predicted — scale the approach.",
            "Consider reinvesting profits into marketing or product improvement.",
            "Evaluate if similar strategies can work in new markets."
        ]
    else:
        return [
            "Results underperformed prediction — review your cost structure.",
            "Reassess pricing and customer acquisition channels.",
            "Run a smaller pilot before full-scale rollout next time."
        ]

def generate_pdf_report(df, avg_pred, avg_act, feedback):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Business Strategy Simulation Report")

    # Average Revenue
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Predicted Average Revenue: ${avg_pred:,.2f}")
    c.drawString(50, height - 100, f"Actual Average Revenue: ${avg_act:,.2f}")

    # Feedback
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 130, "Recommendations:")
    c.setFont("Helvetica", 12)
    y = height - 150
    for tip in feedback:
        c.drawString(60, y, f"- {tip}")
        y -= 20

    # Data Table
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Simulation Data:")
    y -= 20
    c.setFont("Helvetica", 10)
    for i, row in df.iterrows():
        c.drawString(60, y, f"Month {int(row['Month'])} | Predicted: ${row['PredictedRevenue']:,.2f} | Actual: ${row['ActualRevenue']:,.2f} | Cost: ${row['Cost']:,.2f}")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- App navigation ---
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Input Data", "Run Simulation", "Summary"])

# --- Pages ---
if page == "Overview":
    st.title("📊 Business Strategy Simulator")
    st.write("""
    This tool helps you:
    - Plan your business strategy
    - Run a simulation of predicted vs actual outcomes
    - Get automated, actionable feedback
    - Export a professional report
    """)
    st.success("Move to 'Input Data' to start planning your strategy.")

elif page == "Input Data":
    st.title("📥 Input Strategy Details")
    col1, col2 = st.columns(2)
    with col1:
        revenue = st.number_input("Predicted Monthly Revenue ($)", 1000, 1000000, 50000, step=1000)
        cost = st.number_input("Predicted Monthly Cost ($)", 500, 500000, 20000, step=500)
    with col2:
        growth = st.slider("Predicted Monthly Growth Rate (%)", 0.0, 50.0, 5.0)
        months = st.slider("Simulation Period (months)", 1, 36, 12)
    st.session_state["predictions"] = {
        "Revenue": revenue,
        "Cost": cost,
        "GrowthRate": growth,
        "Months": months
    }
    st.success("Data saved. Move to 'Run Simulation'.")

elif page == "Run Simulation":
    st.title("▶ Run Simulation")
    if "predictions" not in st.session_state:
        st.error("Please input your data first in 'Input Data'.")
    else:
        data = st.session_state["predictions"]
        predicted_rev = data["Revenue"]
        predicted_cost = data["Cost"]
        growth_rate = data["GrowthRate"] / 100
        months = data["Months"]

        results = []
        actual_factor = 0.9 + (0.2 * pd.np.random.rand())  # randomness
        for m in range(1, months+1):
            pred = predicted_rev * ((1 + growth_rate) ** (m-1))
            act = pred * actual_factor
            results.append([m, pred, act, data["Cost"]])
        df = pd.DataFrame(results, columns=["Month", "PredictedRevenue", "ActualRevenue", "Cost"])
        st.session_state["results_df"] = df
        st.success("Simulation complete! Check the 'Summary' page.")

elif page == "Summary":
    st.title("📈 Strategy Summary & Insights")
    if "results_df" not in st.session_state:
        st.error("Please run the simulation first.")
    else:
        df = st.session_state["results_df"]
        st.subheader("Performance Chart")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Month"], df["PredictedRevenue"], label="Predicted Revenue", marker="o")
        ax.plot(df["Month"], df["ActualRevenue"], label="Actual Revenue", marker="x")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue ($)")
        ax.legend()
        st.pyplot(fig)

        avg_pred = df["PredictedRevenue"].mean()
        avg_act = df["ActualRevenue"].mean()
        st.subheader("📊 Average Performance")
        st.write(f"**Predicted Avg Revenue:** ${avg_pred:,.2f}")
        st.write(f"**Actual Avg Revenue:** ${avg_act:,.2f}")

        st.subheader("💡 Recommendations")
        feedback = generate_feedback(avg_pred, avg_act)
        for tip in feedback:
            st.write(f"- {tip}")

        st.subheader("📥 Download Results")
        st.markdown(download_link(df, "csv"), unsafe_allow_html=True)
        st.markdown(download_link(df, "excel"), unsafe_allow_html=True)

        pdf_buffer = generate_pdf_report(df, avg_pred, avg_act, feedback)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name="strategy_report.pdf",
            mime="application/pdf"
        )

