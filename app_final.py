import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

# SEITENKONFIGURATION - MUSS DER ERSTE STREAMLIT-BEFEHL SEIN
st.set_page_config(
    page_title="ADC Ressourcendashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEMA
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #009999 !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700; 
    }
    .metric-card {
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #009999;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .critical-alert {
        background: linear-gradient(135deg, #e0f7fa 0%, #e0f2f1 100%);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #00bcd4;
        margin: 0.8rem 0;
        box-shadow: 0 3px 5px rgba(0, 188, 212, 0.3);
        color: #006064 !important;
    }
    .critical-alert h4, .critical-alert p, .critical-alert b {
        color: #006064 !important;
    }
    .section-header {
        color: #009999;
        border-bottom: 2px solid #009999;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        background: linear-gradient(135deg, #009999 0%, #007777 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #007777 0%, #005555 100%);
        color: white;
    }
    .delete-btn {
        background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%) !important;
    }
    .delete-btn:hover {
        background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%) !important;
    }
    .edit-btn {
        background: linear-gradient(135deg, #fa8c16 0%, #ffa940 100%) !important;
    }
    .edit-btn:hover {
        background: linear-gradient(135deg, #ffa940 0%, #fa8c16 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialisiere Session-State für Datenpersistenz
if 'team_data' not in st.session_state:
    st.session_state.team_data = [
        {"name": "Alice Schmidt", "role": "Developer", "components": "DOKU", 
         "start_date": "2020-01-01", "planned_exit": "2026-12-31", "knowledge_transfer_status": "Not Started", "priority": "High", "dob": "1994-05-15", "team": "CS1"},
        {"name": "Bob Weber", "role": "Tester", "components": "Generell", 
         "start_date": "2021-03-15", "planned_exit": "2029-06-30", "knowledge_transfer_status": "In Progress", "priority": "Critical", "dob": "1976-08-20", "team": "CS2"},
        {"name": "Charlie Mueller", "role": "System Architect", "components": "iBS", 
         "start_date": "2019-06-01", "planned_exit": "2025-12-30", "knowledge_transfer_status": "Completed", "priority": "Medium", "dob": "1974-03-10", "team": "CS3"},
        {"name": "Diana Fischer", "role": "Requirements Engineer", "components": "TMS", 
         "start_date": "2022-01-10", "planned_exit": "2031-09-15", "knowledge_transfer_status": "Not Started", "priority": "High", "dob": "1969-11-25", "team": "CS4"},
        {"name": "Erik Wagner", "role": "Scrum Master", "components": "Kundenprojekte", 
         "start_date": "2021-08-20", "planned_exit": "2035-11-30", "knowledge_transfer_status": "In Progress", "priority": "Medium", "dob": "1997-02-14", "team": "CS5"},
        {"name": "Markus Becker", "role": "DevOps Engineer", "components": "Backend, Cloud", "start_date": "2023-02-11", "planned_exit": "2028-12-15", "knowledge_transfer_status": "Not Started", "priority": "Medium", "dob": "1997-07-30", "team": "CS1"},
        {"name": "Sophie Krause", "role": "Business Analyst", "components": "Finanzen, Generell", "start_date": "2018-08-30", "planned_exit": "2027-03-12", "knowledge_transfer_status": "Completed", "priority": "High", "dob": "1985-04-05", "team": "CS2"},
        {"name": "Julia Wagner", "role": "UI/UX Designer", "components": "Frontend, TMS", "start_date": "2021-05-18", "planned_exit": "2026-08-29", "knowledge_transfer_status": "In Progress", "priority": "Critical", "dob": "1990-09-12", "team": "CS3"},
        {"name": "Lars Richter", "role": "Test Automation", "components": "Testing, iBS", "start_date": "2019-11-04", "planned_exit": "2025-11-04", "knowledge_transfer_status": "Not Started", "priority": "Medium", "dob": "1981-12-18", "team": "CS4"},
        {"name": "Heike Zimmermann", "role": "Product Owner", "components": "Kommunikation, Kundenprojekte", "start_date": "2017-03-14", "planned_exit": "2026-09-01", "knowledge_transfer_status": "Completed", "priority": "High", "dob": "1973-06-22", "team": "CS5"} 
    ]

if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None

def main():
    # KOPFZEILE
    st.markdown('<h1 class="main-header">🏢 ADC Ressourcendashboard📈📅</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">MVP</p>', unsafe_allow_html=True)

    
    # Initialize component map
    if 'component_map' not in st.session_state:
        st.session_state.component_map = {}
    # Anzahl benötigter Personen pro Komponente
    if 'component_requirements' not in st.session_state:
        st.session_state.component_requirements = {}

    # Wissensübergabe Zeiten pro Komponente
    if 'component_transfer_times' not in st.session_state:
        st.session_state.component_transfer_times = {}

    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.team_data)
    if not df.empty:
        if 'team' not in df.columns:
            df['team'] = "Unassigned"
        df['planned_exit'] = pd.to_datetime(df['planned_exit'])
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['dob'] = pd.to_datetime(df['dob'])
        df['age'] = pd.Timestamp.today().year - df['dob'].dt.year - ((pd.Timestamp.today().month < df['dob'].dt.month) | ((pd.Timestamp.today().month == df['dob'].dt.month) & (pd.Timestamp.today().day < df['dob'].dt.day)))
        df['days_until_exit'] = (df['planned_exit'] - pd.Timestamp.today()).dt.days
        df['tenure_days'] = (pd.Timestamp.today() - df['start_date']).dt.days
    else:
        # Create empty dataframe with expected columns if no data
        df = pd.DataFrame(columns=['name', 'role', 'components', 'start_date', 'planned_exit', 'knowledge_transfer_status', 'priority'])
    
    # KEY METRICS ROW
    st.markdown("---")
    st.markdown('<h3 class="section-header">📊 Leistungskennzahlen</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_members = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color: #009999;">👥</h3>
            <h2 style="margin:0; color: #009999;">{total_members}</h2>
            <p style="margin:0; color: #666;">Gesamtanzahl Teammitglieder</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical_cases = len(df[df['days_until_exit'] < 180]) if not df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color: #00bcd4;">🚨</h3>
            <h2 style="margin:0; color: #00bcd4;">{critical_cases}</h2>
            <p style="margin:0; color: #666;">Kritische Fälle</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        completed_kt = len(df[df['knowledge_transfer_status'] == "Completed"]) if not df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color: #52c41a;">✅</h3>
            <h2 style="margin:0; color: #52c41a;">{completed_kt}/{total_members}</h2>
            <p style="margin:0; color: #666;">Wissensübergabe abgeschlossen</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_tenure = int(df['tenure_days'].mean() / 365) if not df.empty and 'tenure_days' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color: #fa8c16;">📅</h3>
            <h2 style="margin:0; color: #fa8c16;">{avg_tenure} yrs</h2>
            <p style="margin:0; color: #666;">Durchschnittliche Teamzugehörigkeit</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CRITICAL ALERTS SECTION
    st.markdown("---")
    st.markdown('<h3 class="section-header">🔷 Kritische Ressourcenwarnungen</h3>', unsafe_allow_html=True)
    
    if not df.empty:
        critical_cases = df[df['days_until_exit'] < 180].sort_values('days_until_exit')
        
        if not critical_cases.empty:
            for _, person in critical_cases.iterrows():
                # Turquoise blue color coding based on urgency
                
                if person['days_until_exit'] < 90:
                    urgency_color = "#FF4D4F"  # Red
                    urgency_bg = "#FF4D4F"
                    urgency_text = "EXTREMELY URGENT"
                elif person['days_until_exit'] < 180:
                    urgency_color = "#FFA500"  # Orange
                    urgency_bg = "#FFA500"
                    urgency_text = "URGENT"
                elif person['days_until_exit'] < 365:
                    urgency_color = "#FFD700"  # Gold
                    urgency_bg = "#FFD700"
                    urgency_text = "Monitor"
                else:
                    urgency_color = "#52C41A"  # Green

                
                st.markdown(f"""
                <div class="critical-alert">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin:0; color: {urgency_color};">🔷 {person['name']} - {person['role']}</h4>
                            <p style="margin:0.3rem 0;"><b>Status: {urgency_text} - Leaves in {person['days_until_exit']} days</b></p>
                            <p style="margin:0.3rem 0;">Components: {person['components']}</p>
                            <p style="margin:0.3rem 0;">Wissensübergabe: <b>{person['knowledge_transfer_status']}</b> | Priorität: <b>{person['priority']}</b></p>
                        </div>
                        <div style="background-color: {urgency_bg}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: bold;">
                            {person['days_until_exit']} days
                        </div>
                    </div>
                    <p style="margin:0.5rem 0 0 0; font-style: italic;">💡 Empfohlene Maßnahme: Ressourcenaufbau bald starten</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Keine kritischen Personalengpässe in den nächsten 6 Monaten")
    else:
        st.info("ℹ️ Keine Teamdaten verfügbar. Fügen Sie Teammitglieder hinzu, um kritische Warnungen zu sehen.")
    
    # COMPONENT-SPECIFIC CRITICAL ALERTS (Color-coded)
    if 'component_map' in st.session_state and st.session_state.component_map:
        # Build component status table with required staffing vs active resources
        component_rows = []
        today = pd.Timestamp.today().normalize()
        for component, responsible in st.session_state.component_map.items():
            # Robust active count:
            # - Count rows where member.components contains the component OR member.name is in responsible list
            # normalize responsible to a list
            responsible_list = responsible if isinstance(responsible, (list, tuple)) else [responsible]
            # - Member is active when start_date <= today AND (planned_exit is NaT or planned_exit > today)
            comp_key = component.strip().lower()
            active_count = 0
            for _, row in df.iterrows():
                # normalize fields
                name = str(row.get('name', '')).strip()
                comps_field = row.get('components', '') or ''
                comps = [c.strip().lower() for c in str(comps_field).split(',') if c.strip()]

                # parse dates safely
                try:
                    sd = pd.to_datetime(row['start_date'])
                except Exception:
                    continue
                pe = pd.to_datetime(row.get('planned_exit'))

                started = sd <= today
                not_left = pd.isna(pe) or (pe > today)

                assigned = (comp_key in comps) or (name in responsible_list)
                if assigned and started and not_left:
                    active_count += 1

            required = int(st.session_state.component_requirements.get(component, 1))

            if active_count == 0:
                status = "UNBESETZT"
            elif active_count < required:
                # Single resource available -> critical (red)
                status = "UNTERBESETZT - SINGLE" if active_count == 1 else "UNTERBESETZT"
            else:
                status = "OK"

            component_rows.append({
                "Komponente": component,
                "Verantwortlich": ", ".join(responsible_list),
                "Aktive Ressourcen": active_count,
                "Benötigt": required,
                "Status": status
            })

        comp_df = pd.DataFrame(component_rows).sort_values(["Status", "Komponente"], ascending=[True, True])

        def status_style(val):
            if val == "UNBESETZT":
                return "background-color: #ff4d4f; color: white; font-weight: bold"
            if val == "UNTERBESETZT - SINGLE":
                return "background-color: #ff4d4f; color: white; font-weight: bold"
            if val == "UNTERBESETZT":
                return "background-color: #fa8c16; color: white; font-weight: bold"
            if val == "OK":
                return "background-color: #52c41a; color: white; font-weight: bold"
            return ""

        styled_comp_df = comp_df.style.applymap(lambda v: status_style(v), subset=["Status"])
        st.markdown("#### 🧩 Komponentenübersicht & Staffing-Status")
        st.dataframe(styled_comp_df, use_container_width=True)
    else:
        st.info("ℹ️ Keine Komponenten zugewiesen.")

    # EDIT/DELETE INTERFACE
    st.markdown("---")
    st.markdown('<h3 class="section-header">✏️ Teammitglieder verwalten</h3>', unsafe_allow_html=True)
    
    if not df.empty:
        # Display each team member with edit/delete options
        for i, member in enumerate(st.session_state.team_data):
            with st.expander(f"👤 {member['name']} - {member['role']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Components:** {member['components']}")
                    st.write(f"**Team:** {member.get('team', 'Unassigned')}")
                    # derive components where this member is one of the responsibles
                    assigned_components = []
                    for comp, responsibles in st.session_state.component_map.items():
                        resp_list = responsibles if isinstance(responsibles, (list, tuple)) else [responsibles]
                        if member['name'] in resp_list:
                            assigned_components.append(comp)
                    if assigned_components:
                        st.write(f"**Zugewiesene Komponenten:** {', '.join(assigned_components)}")

                    st.write(f"**Startdatum:** {member['start_date']}")
                    st.write(f"**Planned Exit:** {member['planned_exit']}")
                    st.write(f"**Wissensübergabe:** {member['knowledge_transfer_status']}")
                    st.write(f"**Priorität:** {member['priority']}")
                
                with col2:
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_{i}", use_container_width=True):
                            st.session_state.editing_index = i
                    with col_del:
                        if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True):
                            del st.session_state.team_data[i]
                            st.rerun()
    
    # EDIT FORM (appears when editing)
    if st.session_state.editing_index is not None:
        st.markdown("---")
        st.markdown('<h3 class="section-header">📝 Teammitglied bearbeiten</h3>', unsafe_allow_html=True)
        
        edit_index = st.session_state.editing_index
        member = st.session_state.team_data[edit_index]
        
        with st.form(f"edit_form_{edit_index}"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Vollständiger Name", value=member['name'])
                edit_role = st.text_input("Rolle/Position", value=member['role'])
                edit_components = st.text_area("Wichtige Komponenten/Verantwortlichkeiten", value=member['components'])
            
            with col2:
                edit_start_date = st.date_input("Startdatum", value=datetime.strptime(member['start_date'], "%Y-%m-%d"))
                edit_planned_exit = st.date_input("Geplantes Austrittsdatum", value=datetime.strptime(member['planned_exit'], "%Y-%m-%d"))
                edit_status = st.selectbox("Status der Wissensübergabe", 
                                         ["Not Started", "In Progress", "Completed"],
                                         index=["Not Started", "In Progress", "Completed"].index(member['knowledge_transfer_status']))
                edit_priority = st.selectbox("Prioritätsstufe",
                                           ["Low", "Medium", "High", "Critical"],
                                           index=["Low", "Medium", "High", "Critical"].index(member['priority']))
                # Geburtsdatum hinzufügen / editieren
                edit_dob = st.date_input("Geburtsdatum", value=datetime.strptime(member.get('dob', '1990-01-01'), "%Y-%m-%d"))
                # Team auswählen
                teams = ["CS1", "CS2", "CS3", "CS4", "CS5", "Unassigned"]
                edit_team = st.selectbox("Team", teams, index=teams.index(member.get('team', 'Unassigned')))
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                save_clicked = st.form_submit_button("💾 Änderungen speichern", use_container_width=True)
            with col_cancel:
                cancel_clicked = st.form_submit_button("❌ Abbrechen", use_container_width=True)
            
            if save_clicked:
                st.session_state.team_data[edit_index] = {
                    "name": edit_name,
                    "role": edit_role,
                    "components": edit_components,
                    "start_date": edit_start_date.strftime("%Y-%m-%d"),
                    "planned_exit": edit_planned_exit.strftime("%Y-%m-%d"),
                    "knowledge_transfer_status": edit_status,
                    "priority": edit_priority,
                    "dob": edit_dob.strftime("%Y-%m-%d"),
                    "team": edit_team
                }
                st.session_state.editing_index = None
                st.rerun()
            
            if cancel_clicked:
                st.session_state.editing_index = None
                st.rerun()
    
    # VISUALIZATIONS ROW
    if not df.empty:
        st.markdown("---")
        st.markdown('<h3 class="section-header">📈 Strategische Übersicht</h3>', unsafe_allow_html=True)
        
        # grouping control
        group_by = st.selectbox("Group timeline by", ["Name", "Team"], index=0, help="Wähle, ob die Timeline pro Person oder pro Team gruppiert werden soll.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Timeline Gantt Chart
            y_axis = "name" if group_by == "Name" else "team"
            fig_timeline = px.timeline(df, x_start="start_date", x_end="planned_exit", y=y_axis,
                                     color="priority", 
                                     hover_data=["name", "role"] if y_axis == "team" else ["role"],
                                     title="Zeitplan der Teammitglieder (Farbe nach Priorität)",
                                     color_discrete_map={
                                         "Critical": "#d40000",
                                         "High": "#ED8727", 
                                         "Medium": "#4dd0e1",
                                         "Low": "#4FCA11"
                                     })
            fig_timeline.update_layout(
                height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#333")
            )
            fig_timeline.update_xaxes(gridcolor='#f0f0f0')
            fig_timeline.update_yaxes(gridcolor='#f0f0f0')
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Altersverteilung nach Gruppen (jetzt links)
            if 'age' in df.columns and not df['age'].dropna().empty:
                ages = df['age'].dropna().astype(int)
                # Age groups up to 65 — remove the separate '65+' label
                bins = [0, 24, 34, 44, 54, 64]
                labels = ["<25", "25-34", "35-44", "45-54", "55-64"]
                age_groups = pd.cut(ages, bins=bins, labels=labels, right=True, include_lowest=True)
                age_counts = age_groups.value_counts().reindex(labels).fillna(0).astype(int)
                fig_age = px.bar(
                    x=age_counts.index,
                    y=age_counts.values,
                    labels={'x': 'Altersgruppe', 'y': 'Anzahl'},
                    title="Altersverteilung (Gruppen)"
                )
                fig_age.update_layout(height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("ℹ️ Keine Altersdaten vorhanden.")
        
        with col2:
            # Risk Assessment Donut Chart
            status_counts = df['knowledge_transfer_status'].value_counts()
            fig_donut = px.pie(values=status_counts.values, names=status_counts.index, 
                              title="Status der Wissensübergabe Overview",
                              hole=0.4,
                              color=status_counts.index,
                              color_discrete_map={
                                  "Not Started": "#d40000",
                                  "In Progress": "#4dd0e1", 
                                  "Completed": "#52C41A"
                              })
            fig_donut.update_layout(
                height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#333")
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            
    # Prognose: Forecast for next period with selectable granularity
    st.markdown("---")
    st.markdown("#### 📈 Teamprognose")
    
    # Granularity selector
    granularity = st.selectbox(
        "Granularität wählen:",
        options=["Monatlich", "Quartalsweise", "Jährlich"],
        index=0,
        help="Wählen Sie die Zeitgranularität für die Prognose aus."
    )
    
    # Set freq based on granularity
    if granularity == "Monatlich":
        freq = 'MS'
        x_title = 'Monat'
        title_suffix = 'pro Monat'
    elif granularity == "Quartalsweise":
        freq = 'QS'
        x_title = 'Quartal'
        title_suffix = 'pro Quartal'
    else:  # Jährlich
        freq = 'YS'
        x_title = 'Jahr'
        title_suffix = 'pro Jahr'
    
    # Time period selector with calendar
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Startdatum:",
            value=pd.Timestamp.today().normalize(),
            help="Wählen Sie das Startdatum für die Prognose aus."
        )
    with col2:
        end_date = st.date_input(
            "Enddatum:",
            value=pd.Timestamp.today().normalize() + pd.DateOffset(years=2),
            help="Wählen Sie das Enddatum für die Prognose aus."
        )
    
    # Validate dates
    if start_date >= end_date:
        st.error("Das Startdatum muss vor dem Enddatum liegen.")
        st.stop()
    
    # Calculate periods based on granularity and date range
    start_month = pd.Timestamp(start_date).replace(day=1)
    date_range = pd.date_range(start=start_month, end=end_date, freq=freq)
    periods = len(date_range)
    
    forecast_periods = date_range
    forecast_df = pd.DataFrame({x_title: forecast_periods})

    forecast_df['Aktive Mitglieder'] = forecast_df[x_title].apply(
        lambda m: ((df['start_date'] <= m) & ((df['planned_exit'].isna()) | (df['planned_exit'] > m))).sum()
    )
    forecast_df['Geplante Austritte'] = forecast_df[x_title].apply(
        lambda m: (df['planned_exit'].dt.to_period(freq[0].upper()) == m.to_period(freq[0].upper())).sum()
    )

    fig_forecast = px.line(
        forecast_df,
        x=x_title,
        y=['Aktive Mitglieder', 'Geplante Austritte'],
        labels={'value': 'Anzahl', x_title: x_title, 'variable': 'Metrik'},
        title=f'Teamprognose: Aktive Mitglieder und Austritte {title_suffix}'
    )

    # Add range slider for better navigation when many periods
    fig_forecast.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(fig_forecast, use_container_width=True)

    # Summary chart: Entries and Exits per Year
    years = pd.date_range(start=start_date, end=end_date, freq='YS').year
    summary_data = []
    for year in years:
        entries = ((df['start_date'].dt.year == year)).sum()
        exits = ((df['planned_exit'].dt.year == year)).sum()
        summary_data.append({'Jahr': year, 'Eintritte': entries, 'Austritte': exits})
    
    summary_df = pd.DataFrame(summary_data)
    
    if not summary_df.empty:
        fig_summary = px.bar(
            summary_df,
            x='Jahr',
            y=['Eintritte', 'Austritte'],
            labels={'value': 'Anzahl', 'Jahr': 'Jahr', 'variable': 'Typ'},
            title='Jährliche Eintritte und Austritte',
            barmode='group'
        )
        fig_summary.update_layout(height=300)
        st.plotly_chart(fig_summary, use_container_width=True)

    # Kritische Alerts Tabelle
    critical_df = df[df['days_until_exit'] < 180][['name', 'role', 'components', 'days_until_exit', 'priority']]
    critical_df = critical_df.sort_values('days_until_exit')

    st.markdown("#### 🚨 Kritische Austritte (< 180 Tage)")
    if not critical_df.empty:
        st.dataframe(critical_df, use_container_width=True)
    else:
        st.success("✅ Keine kritischen Austritte in den nächsten 6 Monaten.") # Langere Augenblick , weil Rekrutierunngsphase (ca.3 Monate) laenger braucht.

    # Geburtstagsliste für den aktuellen Monat
    current_month = pd.Timestamp.today().month
    birthday_df = df[df['dob'].dt.month == current_month][['name', 'role', 'dob', 'age']]
    birthday_df = birthday_df.sort_values('dob')

    st.markdown("#### 🎂 Geburtstage diesen Monat")
    if not birthday_df.empty:
        st.dataframe(birthday_df, use_container_width=True)
    else:
        st.info("ℹ️ Keine Geburtstage in diesem Monat.")

    # DISPLAY COMPONENT RESPONSIBILITIES TABLE
    if 'component_map' in st.session_state and st.session_state.component_map:
        st.markdown("---")
        st.markdown("#### 🧪 Komponentenübersicht (Kurz)")
        # create a compact view: Komponente, Verantwortlich, Benötigt
        comp_list = []
        transfer_alerts = []
        for comp, resp in st.session_state.component_map.items():
            needed = int(st.session_state.component_requirements.get(comp, 1))
            transfer_months = int(st.session_state.component_transfer_times.get(comp, 6))
            resp_list = resp if isinstance(resp, (list, tuple)) else [resp]
            comp_list.append({"Komponente": comp, "Verantwortlich": ", ".join(resp_list), "Benötigt": needed, "WU-Zeit (Monate)": transfer_months})
            
            # Check for transfer alerts
            for person in resp_list:
                person_data = df[df['name'] == person]
                if not person_data.empty:
                    days_left = person_data['days_until_exit'].iloc[0]
                    if days_left < transfer_months * 30:
                        transfer_alerts.append({
                            "Komponente": comp,
                            "Verantwortlich": person,
                            "Tage bis Austritt": days_left,
                            "Benötigte WU-Zeit (Tage)": transfer_months * 30
                        })
        
        short_comp_df = pd.DataFrame(comp_list)
        st.dataframe(short_comp_df, use_container_width=True)
        
        # Transfer Alerts
        if transfer_alerts:
            st.markdown("#### 🚨 Wissensübergabe-Alerts")
            alert_df = pd.DataFrame(transfer_alerts)
            st.dataframe(alert_df, use_container_width=True)
            st.warning("⚠️ Diese Personen verlassen das Unternehmen, bevor die Wissensübergabe abgeschlossen werden kann. Planen Sie Einstellungen oder Ersatz!")
    else:
        st.info("ℹ️ Noch keine Komponenten hinzugefügt.")

    # DATA TABLE WITH FILTERS
    if not df.empty:
        st.markdown("---")
        st.markdown('<h3 class="section-header">👥 Detaillierte Teamübersicht</h3>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            status_filter = st.multiselect("Wissensübergabe", 
                                         options=df['knowledge_transfer_status'].unique(),
                                         default=df['knowledge_transfer_status'].unique())
        with col2:
            priority_filter = st.multiselect("Prioritätsstufe",
                                           options=df['priority'].unique(),
                                           default=df['priority'].unique())
        with col3:
            role_filter = st.multiselect("Rolle",
                                       options=df['role'].unique(),
                                       default=df['role'].unique())
        with col4:
            days_filter = st.slider("Tage bis Austritt", 
                                  min_value=0, 
                                  max_value=int(df['days_until_exit'].max()) + 100 if not df.empty else 1000,
                                  value=(0, 1000))
        with col5:
            team_options = sorted(df['team'].unique())
            team_filter = st.multiselect("Team", options=team_options, default=team_options)
        
        # filters
        filtered_df = df[
            (df['knowledge_transfer_status'].isin(status_filter)) &
            (df['priority'].isin(priority_filter)) &
            (df['role'].isin(role_filter)) &
            (df['days_until_exit'] >= days_filter[0]) &
            (df['days_until_exit'] <= days_filter[1]) &
            (df['team'].isin(team_filter))
        ]
        
        # Display filtered table
        display_df = filtered_df[['name', 'role', 'team', 'components', 'priority', 'days_until_exit', 'knowledge_transfer_status']].copy()
        display_df.columns = ['Name', 'Rolle', 'Team', 'Components', 'Priorität', 'Tage bis Austritt', 'WU-Status']
        
        # Color code the Tage bis Austritt column
        def color_days(val):
            if val < 90:
                color = '#00bcd4'
            elif val < 180:
                color = '#4dd0e1'
            else:
                color = '#52c41a'
            return f'color: {color}; font-weight: bold'
        
        styled_df = display_df.style.applymap(color_days, subset=['Tage bis Austritt'])
        st.dataframe(styled_df, use_container_width=True)
    
    # ADD NEW MEMBER FORM IN SIDEBAR
    st.sidebar.markdown('<h3 style="color: #009999;">➕ Teammitglied hinzufügen</h3>', unsafe_allow_html=True)
    
    with st.sidebar.form("add_member", clear_on_submit=True):
        name = st.text_input("Vollständiger Name")
        role = st.text_input("Rolle/Position")
        components = st.text_area("Wichtige Komponenten/Verantwortlichkeiten")
        dob = st.date_input("Geburtsdatum", value=datetime(1990, 1, 1))
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Startdatum", value=datetime.now())
        with col2:
            planned_exit = st.date_input("Planned Exit", value=datetime.now() + timedelta(days=365))
        
        col3, col4 = st.columns(2)
        with col3:
            status = st.selectbox("Wissensübergabe", ["Not Started", "In Progress", "Completed"])
        with col4:
            priority = st.selectbox("Priorität", ["Low", "Medium", "High", "Critical"])
        # Team Auswahl
        team = st.selectbox("Team", ["CS1", "CS2", "CS3", "CS4", "CS5", "Unassigned"], index=5)
        
        submitted = st.form_submit_button("💾 Teammitglied hinzufügen", use_container_width=True)
        if submitted:
            if name and role:
                new_member = {
                    "name": name,
                    "role": role,
                    "components": components,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "planned_exit": planned_exit.strftime("%Y-%m-%d"),
                    "knowledge_transfer_status": status,
                    "priority": priority,
                    "dob": dob.strftime("%Y-%m-%d"),
                    "team": team
                }
                st.session_state.team_data.append(new_member)
                st.rerun()
            else:
                st.sidebar.error("Please fill at least Name and Rolle")
    # COMPONENT ASSIGNMENT FORM IN SIDEBAR
    if 'component_map' not in st.session_state:
        st.session_state.component_map = {}

    st.sidebar.markdown('#### 🧪 Neue Komponente hinzufügen')
    with st.sidebar.form("add_component_form", clear_on_submit=True):
        component_name = st.text_input("Komponentenname")
        responsible_persons = st.multiselect("Verantwortliche Person(en)", options=[member['name'] for member in st.session_state.team_data])
        required_count = st.number_input("Benötigte Anzahl Personen (permanent)", min_value=1, max_value=10, value=1)
        transfer_time = st.number_input("Wissensübergabe Zeit (Monate)", min_value=1, max_value=24, value=6)
        component_submitted = st.form_submit_button("💾 Komponente speichern", use_container_width=True)

        if component_submitted:
            if component_name and responsible_persons:
                # store as list
                st.session_state.component_map[component_name] = responsible_persons
                st.session_state.component_requirements[component_name] = int(required_count)
                st.session_state.component_transfer_times[component_name] = int(transfer_time)
                st.sidebar.success(f"✅ '{component_name}' wurde {', '.join(responsible_persons)} zugewiesen.")
            else:
                st.sidebar.error("Bitte geben Sie einen Namen und wählen Sie eine verantwortliche Person aus.")

    # SIDEBAR ACTIONS
    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #009999;">🛠️ Aktionen</h3>', unsafe_allow_html=True) 
    
    if st.sidebar.button("📊 Exportieren nach Excel", use_container_width=True):
        # Create downloadable Excel file
        if not df.empty:
            df.to_excel("siemens_capacity_plan.xlsx", index=False)
            st.sidebar.success("✅ Excel-Datei exportiert als 'siemens_capacity_plan.xlsx'")
        else:
            st.sidebar.error("Keine Daten zum Exportieren")
    
    if st.sidebar.button("🗑️ Alle Daten löschen", use_container_width=True):
        st.session_state.team_data = []
        st.session_state.editing_index = None
        st.rerun()
    
    # SIDEBAR STATS
    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #009999;">📈 Schnellstatistiken</h3>', unsafe_allow_html=True)
    
    if not df.empty:
        st.sidebar.metric("Gesamtes Team", len(df))
        st.sidebar.metric("Gefährdet", len(df[df['days_until_exit'] < 180]))
        st.sidebar.metric("Durchschnittliche Austrittstage", f"{int(df['days_until_exit'].mean())}d")
    else:
        st.sidebar.write("Keine Daten verfügbar")

if __name__ == "__main__":
    main()