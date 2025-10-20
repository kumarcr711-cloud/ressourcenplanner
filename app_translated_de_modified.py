import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go

# SEITENKONFIGURATION - MUSS DER ERSTE STREAMLIT-BEFEHL SEIN
st.set_page_config(
    page_title="ADC Ressourcenplanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BENUTZERDEFINIERTES CSS MIT TÜRKISBLAUEM KRITISCHEM THEMA
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
        {"name": "Alice Schmidt", "role": "Senior Backend Developer", "components": "Payment API, Database", 
         "start_date": "2020-01-01", "planned_exit": "2024-12-31", "knowledge_transfer_status": "Not Started", "priority": "High"},
        {"name": "Bob Weber", "role": "Frontend Developer", "components": "User Interface, React Components", 
         "start_date": "2021-03-15", "planned_exit": "2024-06-30", "knowledge_transfer_status": "In Progress", "priority": "Critical"},
        {"name": "Charlie Mueller", "role": "System Architect", "components": "System Design, Cloud Infrastructure", 
         "start_date": "2019-06-01", "planned_exit": "2025-03-01", "knowledge_transfer_status": "Completed", "priority": "Medium"},
        {"name": "Diana Fischer", "role": "QA Engineer", "components": "Testing Framework, Automation", 
         "start_date": "2022-01-10", "planned_exit": "2024-09-15", "knowledge_transfer_status": "Not Started", "priority": "High"},
        {"name": "Erik Wagner", "role": "DevOps Engineer", "components": "CI/CD Pipeline, Kubernetes", 
         "start_date": "2021-08-20", "planned_exit": "2024-11-30", "knowledge_transfer_status": "In Progress", "priority": "Medium"}
    ]

if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None

def main():
    # KOPFZEILE
    st.markdown('<h1 class="main-header">🏢 ADC TMS Ressourcenplanner</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Besser als Talevo auf jeden Fall</p>', unsafe_allow_html=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.team_data)
    if not df.empty:
        df['planned_exit'] = pd.to_datetime(df['planned_exit'])
        df['start_date'] = pd.to_datetime(df['start_date'])
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
                    urgency_color = "#006064"  # Dark turquoise
                    urgency_bg = "#00bcd4"     # Bright turquoise
                    urgency_text = "EXTREMELY URGENT"
                elif person['days_until_exit'] < 180:
                    urgency_color = "#00838f"  # Medium turquoise
                    urgency_bg = "#4dd0e1"     # Light turquoise
                    urgency_text = "URGENT"
                
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
                    <p style="margin:0.5rem 0 0 0; font-style: italic;">💡 Empfohlene Maßnahme: Einstellungsprozess sofort starten</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Keine kritischen Personalengpässe in den nächsten 6 Monaten")
    else:
        st.info("ℹ️ Keine Teamdaten verfügbar. Fügen Sie Teammitglieder hinzu, um kritische Warnungen zu sehen.")
    
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
                    "priority": edit_priority
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced Timeline Gantt Chart
            fig_timeline = px.timeline(df, x_start="start_date", x_end="planned_exit", y="name",
                                     color="priority", 
                                     title="Zeitplan der Teammitglieder (Farbe nach Priorität)",
                                     color_discrete_map={
                                         "Critical": "#00bcd4",
                                         "High": "#009999", 
                                         "Medium": "#4dd0e1",
                                         "Low": "#52C41A"
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
        
        with col2:
            # Risk Assessment Donut Chart
            status_counts = df['knowledge_transfer_status'].value_counts()
            fig_donut = px.pie(values=status_counts.values, names=status_counts.index, 
                              title="Status der Wissensübergabe Overview",
                              hole=0.4,
                              color=status_counts.index,
                              color_discrete_map={
                                  "Not Started": "#00bcd4",
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
    
    # DATA TABLE WITH FILTERS
    if not df.empty:
        st.markdown("---")
        st.markdown('<h3 class="section-header">👥 Detaillierte Teamübersicht</h3>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
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
        
        # Apply filters
        filtered_df = df[
            (df['knowledge_transfer_status'].isin(status_filter)) &
            (df['priority'].isin(priority_filter)) &
            (df['role'].isin(role_filter)) &
            (df['days_until_exit'] >= days_filter[0]) &
            (df['days_until_exit'] <= days_filter[1])
        ]
        
        # Display filtered table with better formatting
        display_df = filtered_df[['name', 'role', 'components', 'priority', 'days_until_exit', 'knowledge_transfer_status']].copy()
        display_df.columns = ['Name', 'Rolle', 'Components', 'Priorität', 'Tage bis Austritt', 'WU-Status']
        
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
                    "priority": priority
                }
                st.session_state.team_data.append(new_member)
                st.rerun()
            else:
                st.sidebar.error("Please fill at least Name and Rolle")
    
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