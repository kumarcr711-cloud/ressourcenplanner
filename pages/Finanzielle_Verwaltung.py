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
        "Intern": {"monthly_cost": 1500, "yearly_budget": 18000, "hourly_rate": 75, "weekly_hours": 40},
        "Lead Cost Employee (LCE)": {"monthly_cost": 5000, "yearly_budget": 60000, "hourly_rate": 0, "weekly_hours": 0},
        "Extern": {"monthly_cost": 7000, "yearly_budget": 84000, "hourly_rate": 0, "weekly_hours": 0}
    }

# Initialize individual employee settings if not exists
if 'employee_settings' not in st.session_state:
    st.session_state.employee_settings = {}

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
    
    for idx, row in df.iterrows():
        emp_name = row['name']
        emp_type = row['employee_type']
        
        # Check if this is an internal employee with custom settings
        if emp_type == "Intern" and emp_name in st.session_state.employee_settings:
            settings = st.session_state.employee_settings[emp_name]
            hourly_rate = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
            weekly_hours = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
            
            # Calculate monthly cost: (weekly_hours * hourly_rate * 52 weeks) / 12 months
            monthly_cost = (weekly_hours * hourly_rate * 52) / 12
            yearly_budget = weekly_hours * hourly_rate * 52
        else:
            monthly_cost = st.session_state.budget_data[emp_type]["monthly_cost"]
            yearly_budget = st.session_state.budget_data[emp_type]["yearly_budget"]
        
        total_monthly_cost += monthly_cost
        total_yearly_budget += yearly_budget
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monatliche Gesamtkosten", f"€{total_monthly_cost:,.2f}")
    with col2:
        st.metric("Jährliches Budget", f"€{total_yearly_budget:,.2f}")
    with col3:
        st.metric("Anzahl Mitarbeiter", len(df))

# Budget per employee type
st.markdown("---")
st.markdown("### 💼 Kosten pro Mitarbeitertyp")

budget_df = pd.DataFrame.from_dict(st.session_state.budget_data, orient='index')
budget_df['Anzahl'] = budget_df.index.map(employee_counts) if not df.empty else 0

# Calculate actual costs considering custom employee settings
actual_costs = {}
for emp_type in budget_df.index:
    if emp_type == "Intern":
        # Calculate for internal employees with possible custom settings
        intern_employees = df[df['employee_type'] == 'Intern']
        type_monthly_cost = 0
        type_yearly_cost = 0
        for idx, row in intern_employees.iterrows():
            emp_name = row['name']
            if emp_name in st.session_state.employee_settings:
                settings = st.session_state.employee_settings[emp_name]
                hr = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
                wh = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
                type_monthly_cost += (wh * hr * 52) / 12
                type_yearly_cost += wh * hr * 52
            else:
                type_monthly_cost += st.session_state.budget_data[emp_type]["monthly_cost"]
                type_yearly_cost += st.session_state.budget_data[emp_type]["yearly_budget"]
        actual_costs[emp_type] = {'monthly': type_monthly_cost, 'yearly': type_yearly_cost}
    else:
        count = budget_df.loc[emp_type, 'Anzahl']
        actual_costs[emp_type] = {
            'monthly': st.session_state.budget_data[emp_type]["monthly_cost"] * count,
            'yearly': st.session_state.budget_data[emp_type]["yearly_budget"] * count
        }

budget_df['Gesamtkosten (Monat)'] = budget_df.index.map(lambda x: actual_costs[x]['monthly'])
budget_df['Gesamtkosten (Jahr)'] = budget_df.index.map(lambda x: actual_costs[x]['yearly'])

st.dataframe(budget_df[['Anzahl', 'monthly_cost', 'Gesamtkosten (Monat)', 'yearly_budget', 'Gesamtkosten (Jahr)']].rename(columns={
    'monthly_cost': 'Monatliche Kosten pro Person (€)',
    'yearly_budget': 'Jährliche Kosten pro Person (€)'
}))

# Employee cost breakdown
st.markdown("---")
st.markdown("### 👥 Mitarbeiterkosten-Übersicht")

if not df.empty:
    # Add cost columns to the dataframe
    def get_employee_cost(row):
        emp_name = row['name']
        emp_type = row['employee_type']
        
        if emp_type == "Intern" and emp_name in st.session_state.employee_settings:
            settings = st.session_state.employee_settings[emp_name]
            hr = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
            wh = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
            return (wh * hr * 52) / 12
        else:
            return st.session_state.budget_data.get(emp_type, {}).get('monthly_cost', 0)
    
    def get_employee_yearly(row):
        emp_name = row['name']
        emp_type = row['employee_type']
        
        if emp_type == "Intern" and emp_name in st.session_state.employee_settings:
            settings = st.session_state.employee_settings[emp_name]
            hr = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
            wh = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
            return wh * hr * 52
        else:
            return st.session_state.budget_data.get(emp_type, {}).get('yearly_budget', 0)
    
    df['Monatliche Kosten'] = df.apply(get_employee_cost, axis=1)
    df['Jährliche Kosten'] = df.apply(get_employee_yearly, axis=1)
    
    # Display employee list with costs
    cost_df = df[['name', 'role', 'employee_type', 'Monatliche Kosten', 'Jährliche Kosten']].copy()
    cost_df.columns = ['Name', 'Rolle', 'Typ', 'Monatliche Kosten (€)', 'Jährliche Kosten (€)']
    
    # Format currency
    cost_df['Monatliche Kosten (€)'] = cost_df['Monatliche Kosten (€)'].apply(lambda x: f"€{x:,.2f}")
    cost_df['Jährliche Kosten (€)'] = cost_df['Jährliche Kosten (€)'].apply(lambda x: f"€{x:,.2f}")
    
    st.dataframe(cost_df, use_container_width=True)
    
    # Summary by employee type
    st.markdown("#### Zusammenfassung nach Mitarbeitertyp")
    
    # Recalculate summary with actual costs
    summary_data = []
    for emp_type in st.session_state.budget_data.keys():
        type_employees = df[df['employee_type'] == emp_type]
        if not type_employees.empty:
            monthly_sum = 0
            yearly_sum = 0
            for idx, row in type_employees.iterrows():
                emp_name = row['name']
                if emp_type == "Intern" and emp_name in st.session_state.employee_settings:
                    settings = st.session_state.employee_settings[emp_name]
                    hr = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
                    wh = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
                    monthly_sum += (wh * hr * 52) / 12
                    yearly_sum += wh * hr * 52
                else:
                    monthly_sum += st.session_state.budget_data[emp_type]["monthly_cost"]
                    yearly_sum += st.session_state.budget_data[emp_type]["yearly_budget"]
            
            summary_data.append({
                'Typ': emp_type,
                'Anzahl': len(type_employees),
                'Monatliche Kosten (€)': f"€{monthly_sum:,.2f}",
                'Jährliche Kosten (€)': f"€{yearly_sum:,.2f}"
            })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
else:
    st.info("Keine Mitarbeiterdaten verfügbar.")

# Budget adjustment form
st.sidebar.markdown("### ⚙️ Budget anpassen")

with st.sidebar.form("adjust_budget"):
    st.markdown("#### Kategorien-Standard Kosten")
    emp_type = st.selectbox("Mitarbeitertyp", list(st.session_state.budget_data.keys()))
    new_monthly = st.number_input("Monatliche Kosten (€)", value=st.session_state.budget_data[emp_type]["monthly_cost"], min_value=0)
    new_yearly = st.number_input("Jährliche Kosten (€)", value=st.session_state.budget_data[emp_type]["yearly_budget"], min_value=0)
    
    # For Intern category, also show hourly rate and weekly hours
    if emp_type == "Intern":
        st.markdown("#### Stundenmodell für Interne (optional)")
        new_hourly_rate = st.number_input("Stundensatz (€/h)", value=st.session_state.budget_data[emp_type].get("hourly_rate", 75), min_value=0)
        new_weekly_hours = st.number_input("Wöchentliche Stunden", value=st.session_state.budget_data[emp_type].get("weekly_hours", 40), min_value=0)
    
    adjust_submitted = st.form_submit_button("💾 Aktualisieren")
    if adjust_submitted:
        st.session_state.budget_data[emp_type]["monthly_cost"] = new_monthly
        st.session_state.budget_data[emp_type]["yearly_budget"] = new_yearly
        if emp_type == "Intern":
            st.session_state.budget_data[emp_type]["hourly_rate"] = new_hourly_rate
            st.session_state.budget_data[emp_type]["weekly_hours"] = new_weekly_hours
        st.rerun()

# Individual Employee Settings for Interns
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Interne Mitarbeiter - Stundenmodell")

if not df.empty:
    intern_employees = df[df['employee_type'] == 'Intern']
    if not intern_employees.empty:
        selected_intern = st.sidebar.selectbox(
            "Mitarbeiter wählen",
            intern_employees['name'].tolist()
        )
        
        with st.sidebar.form("employee_settings_form"):
            st.markdown(f"**{selected_intern}**")
            
            # Get current or default values
            if selected_intern in st.session_state.employee_settings:
                current_settings = st.session_state.employee_settings[selected_intern]
                current_hourly_rate = float(current_settings.get('hourly_rate', st.session_state.budget_data['Intern']['hourly_rate']))
                current_weekly_hours = int(current_settings.get('weekly_hours', st.session_state.budget_data['Intern']['weekly_hours']))
            else:
                current_hourly_rate = float(st.session_state.budget_data['Intern']['hourly_rate'])
                current_weekly_hours = int(st.session_state.budget_data['Intern']['weekly_hours'])
            
            emp_hourly_rate = st.number_input(
                f"Stundensatz für {selected_intern} (€/h)",
                value=current_hourly_rate,
                min_value=0.0,
                step=0.5,
                key=f"hourly_{selected_intern}"
            )
            emp_weekly_hours = st.number_input(
                f"Wöchentliche Stunden für {selected_intern}",
                value=current_weekly_hours,
                min_value=0,
                step=1,
                key=f"weekly_{selected_intern}"
            )
            
            # Calculate and display projected costs
            if emp_hourly_rate > 0 and emp_weekly_hours > 0:
                projected_monthly = (emp_weekly_hours * emp_hourly_rate * 52) / 12
                projected_yearly = emp_weekly_hours * emp_hourly_rate * 52
                st.info(f"📊 Monatlich: €{projected_monthly:,.2f} | Jährlich: €{projected_yearly:,.2f}")
            
            emp_settings_submitted = st.form_submit_button("💾 Speichern")
            if emp_settings_submitted:
                st.session_state.employee_settings[selected_intern] = {
                    'hourly_rate': emp_hourly_rate,
                    'weekly_hours': emp_weekly_hours
                }
                st.rerun()
    else:
        st.sidebar.info("Keine internen Mitarbeiter vorhanden")

# Additional financial features can be added here
st.markdown("---")
st.markdown("### 📈 Personal- und Kostenprognose")

if not df.empty:
    # Granularity selection and date range
    col1, col2, col3 = st.columns(3)
    
    with col1:
        granularity = st.selectbox(
            "Zeitliche Granularität",
            ["Monatlich", "Quartalsweise", "Jährlich"],
            index=1  # Default to quarterly
        )
    
    with col2:
        start_date = st.date_input(
            "Startdatum",
            value=pd.Timestamp.today()
        )
    
    with col3:
        # Set default end date based on granularity
        if granularity == "Monatlich":
            default_end = pd.Timestamp.today() + pd.DateOffset(years=3)
        elif granularity == "Quartalsweise":
            default_end = pd.Timestamp.today() + pd.DateOffset(years=3)
        else:  # Jährlich
            default_end = pd.Timestamp.today() + pd.DateOffset(years=5)
        
        end_date = st.date_input(
            "Enddatum",
            value=default_end
        )
    
    # Validate date range
    start_date = pd.Timestamp(start_date).normalize()
    end_date = pd.Timestamp(end_date).normalize()
    
    if start_date >= end_date:
        st.error("⚠️ Enddatum muss nach dem Startdatum liegen!")
        st.stop()
    
    # Set frequency based on granularity
    if granularity == "Monatlich":
        freq = 'M'
    elif granularity == "Quartalsweise":
        freq = 'Q'
    else:  # Jährlich
        freq = 'Y'
    
    # Create forecast period with custom date range
    date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
    
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
        
        # Calculate costs with consideration for individual settings
        monthly_cost = 0
        yearly_cost = 0
        
        for emp_type in st.session_state.budget_data.keys():
            if emp_type == "Intern":
                # Calculate for internal employees considering individual settings
                intern_at_date = active_employees[active_employees['employee_type'] == 'Intern']
                for idx, row in intern_at_date.iterrows():
                    emp_name = row['name']
                    if emp_name in st.session_state.employee_settings:
                        settings = st.session_state.employee_settings[emp_name]
                        hr = settings.get('hourly_rate', st.session_state.budget_data[emp_type]['hourly_rate'])
                        wh = settings.get('weekly_hours', st.session_state.budget_data[emp_type]['weekly_hours'])
                        monthly_cost += (wh * hr * 52) / 12
                        yearly_cost += wh * hr * 52
                    else:
                        monthly_cost += st.session_state.budget_data[emp_type]["monthly_cost"]
                        yearly_cost += st.session_state.budget_data[emp_type]["yearly_budget"]
            else:
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