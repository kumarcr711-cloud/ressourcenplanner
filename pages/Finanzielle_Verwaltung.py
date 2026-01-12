import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Finanzielle Verwaltung",
    page_icon="💰",
    layout="wide"
)

# Initialize financial data
if 'budget_data' not in st.session_state:
    st.session_state.budget_data = {
        "Intern": {"monthly_cost": 1500, "yearly_budget": 18000},
        "Lead Cost Employee (LCE)": {"monthly_cost": 5000, "yearly_budget": 60000},
        "Extern": {"monthly_cost": 7000, "yearly_budget": 84000}
    }

# Check if team_data exists
if 'team_data' not in st.session_state:
    st.error("Teamdaten nicht gefunden. Bitte zuerst die Organisationsseite besuchen.")
    st.stop()

st.title("💰 Finanzielle Verwaltung")
st.markdown("Budgetverfolgung und -berechnung für die Abteilung")

# Financial Dashboard
st.markdown("---")
st.markdown("### 📊 Budgetübersicht")

# Calculate current costs
df = pd.DataFrame(st.session_state.team_data)
if not df.empty:
    employee_counts = df['employee_type'].value_counts()
    total_monthly_cost = 0
    total_yearly_budget = 0
    for emp_type, count in employee_counts.items():
        if emp_type in st.session_state.budget_data:
            total_monthly_cost += st.session_state.budget_data[emp_type]["monthly_cost"] * count
            total_yearly_budget += st.session_state.budget_data[emp_type]["yearly_budget"] * count
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monatliche Gesamtkosten", f"€{total_monthly_cost:,}")
    with col2:
        st.metric("Jährliches Budget", f"€{total_yearly_budget:,}")
    with col3:
        st.metric("Anzahl Mitarbeiter", len(df))

# Budget per employee type
st.markdown("---")
st.markdown("### 💼 Kosten pro Mitarbeitertyp")

budget_df = pd.DataFrame.from_dict(st.session_state.budget_data, orient='index')
budget_df['Anzahl'] = budget_df.index.map(employee_counts) if not df.empty else 0
budget_df['Gesamtkosten (Monat)'] = budget_df['monthly_cost'] * budget_df['Anzahl']
budget_df['Gesamtkosten (Jahr)'] = budget_df['yearly_budget'] * budget_df['Anzahl']
st.dataframe(budget_df[['Anzahl', 'monthly_cost', 'Gesamtkosten (Monat)', 'yearly_budget', 'Gesamtkosten (Jahr)']].rename(columns={
    'monthly_cost': 'Monatliche Kosten pro Person (€)',
    'yearly_budget': 'Jährliche Kosten pro Person (€)'
}))

# Employee cost breakdown
st.markdown("---")
st.markdown("### 👥 Mitarbeiterkosten-Übersicht")

if not df.empty:
    # Add cost columns to the dataframe
    df['Monatliche Kosten'] = df['employee_type'].map(lambda x: st.session_state.budget_data.get(x, {}).get('monthly_cost', 0))
    df['Jährliche Kosten'] = df['employee_type'].map(lambda x: st.session_state.budget_data.get(x, {}).get('yearly_budget', 0))
    
    # Display employee list with costs
    cost_df = df[['name', 'role', 'employee_type', 'Monatliche Kosten', 'Jährliche Kosten']].copy()
    cost_df.columns = ['Name', 'Rolle', 'Typ', 'Monatliche Kosten (€)', 'Jährliche Kosten (€)']
    st.dataframe(cost_df)
    
    # Summary by employee type
    st.markdown("#### Zusammenfassung nach Mitarbeitertyp")
    summary = cost_df.groupby('Typ').agg({
        'Monatliche Kosten (€)': 'sum',
        'Jährliche Kosten (€)': 'sum',
        'Name': 'count'
    }).rename(columns={'Name': 'Anzahl'})
    st.dataframe(summary)
else:
    st.info("Keine Mitarbeiterdaten verfügbar.")

# Budget adjustment form
st.sidebar.markdown("### ⚙️ Budget anpassen")

with st.sidebar.form("adjust_budget"):
    emp_type = st.selectbox("Mitarbeitertyp", list(st.session_state.budget_data.keys()))
    new_monthly = st.number_input("Monatliche Kosten (€)", value=st.session_state.budget_data[emp_type]["monthly_cost"], min_value=0)
    new_yearly = st.number_input("Jährliche Kosten (€)", value=st.session_state.budget_data[emp_type]["yearly_budget"], min_value=0)
    adjust_submitted = st.form_submit_button("💾 Aktualisieren")
    if adjust_submitted:
        st.session_state.budget_data[emp_type]["monthly_cost"] = new_monthly
        st.session_state.budget_data[emp_type]["yearly_budget"] = new_yearly
        st.rerun()

# Additional financial features can be added here
st.markdown("---")
st.markdown("### 📈 Personal- und Kostenprognose")

if not df.empty:
    # Granularity selection
    granularity = st.selectbox(
        "Zeitliche Granularität",
        ["Monatlich", "Quartalsweise", "Jährlich"],
        index=1  # Default to quarterly
    )
    
    # Set frequency based on granularity
    if granularity == "Monatlich":
        freq = 'M'
        periods = 36  # 3 years
    elif granularity == "Quartalsweise":
        freq = 'Q'
        periods = 12  # 3 years
    else:  # Jährlich
        freq = 'Y'
        periods = 5   # 5 years
    
    # Create forecast period
    start_date = pd.Timestamp.today().normalize()
    date_range = pd.date_range(start=start_date, periods=periods, freq=freq)
    
    # Initialize forecast data
    forecast_data = []
    
    for date in date_range:
        # Count active employees at this date
        active_employees = df[
            (pd.to_datetime(df['start_date']) <= date) & 
            (pd.to_datetime(df['planned_exit']) >= date)
        ]
        
        # Count by employee type
        type_counts = active_employees['employee_type'].value_counts()
        
        # Calculate costs
        monthly_cost = 0
        yearly_cost = 0
        for emp_type in st.session_state.budget_data.keys():
            count = type_counts.get(emp_type, 0)
            monthly_cost += st.session_state.budget_data[emp_type]["monthly_cost"] * count
            yearly_cost += st.session_state.budget_data[emp_type]["yearly_budget"] * count
        
        forecast_data.append({
            'Datum': date,
            'Gesamt_Mitarbeiter': len(active_employees),
            'Intern': type_counts.get('Intern', 0),
            'Lead Cost Employee (LCE)': type_counts.get('Lead Cost Employee (LCE)', 0),
            'Extern': type_counts.get('Extern', 0),
            'Monatliche_Kosten': monthly_cost,
            'Jährliche_Kosten': yearly_cost
        })
    
    forecast_df = pd.DataFrame(forecast_data)
    
    # Employee Count Chart
    st.markdown("#### 👥 Mitarbeiterentwicklung")
    fig_employees = px.line(
        forecast_df, 
        x='Datum', 
        y=['Gesamt_Mitarbeiter', 'Intern', 'Lead Cost Employee (LCE)', 'Extern'],
        title=f"Mitarbeiterprognose ({granularity})",
        labels={'value': 'Anzahl Mitarbeiter', 'variable': 'Kategorie'}
    )
    fig_employees.update_layout(
        xaxis_title="Zeitraum",
        yaxis_title="Anzahl Mitarbeiter",
        legend_title="Legende"
    )
    st.plotly_chart(fig_employees, use_container_width=True)
    
    # Cost Chart
    st.markdown("#### 💰 Kostenentwicklung")
    if granularity == "Monatlich":
        cost_col = 'Monatliche_Kosten'
        cost_title = "Monatliche Kosten"
    elif granularity == "Quartalsweise":
        # For quarterly, show quarterly costs (3 months)
        forecast_df['Quartalskosten'] = forecast_df['Monatliche_Kosten'] * 3
        cost_col = 'Quartalskosten'
        cost_title = "Quartalskosten"
    else:  # Jährlich
        cost_col = 'Jährliche_Kosten'
        cost_title = "Jährliche Kosten"
    
    fig_costs = px.line(
        forecast_df, 
        x='Datum', 
        y=cost_col,
        title=f"Kostenprognose ({cost_title})",
        labels={'value': f'{cost_title} (€)'}
    )
    fig_costs.update_layout(
        xaxis_title="Zeitraum",
        yaxis_title=f"{cost_title} (€)"
    )
    # Format y-axis as currency
    fig_costs.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig_costs, use_container_width=True)
    
    # Forecast Summary Table
    st.markdown("#### 📊 Prognosedaten")
    display_cols = ['Datum', 'Gesamt_Mitarbeiter', 'Intern', 'Lead Cost Employee (LCE)', 'Extern', cost_col]
    display_df = forecast_df[display_cols].copy()
    display_df.columns = ['Datum', 'Gesamt', 'Intern', 'LCE', 'Extern', f'{cost_title} (€)']
    display_df[f'{cost_title} (€)'] = display_df[f'{cost_title} (€)'].apply(lambda x: f"€{x:,.0f}")
    st.dataframe(display_df, use_container_width=True)
    
else:
    st.info("Keine Daten für Prognose verfügbar.")