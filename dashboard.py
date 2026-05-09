import streamlit as st
import sqlalchemy
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import analyze_db
import warnings
warnings.filterwarnings('ignore')

DB_URL = "sqlite:///patents.db"

st.set_page_config(page_title="Global Patent Intelligence Dashboard", page_icon="📜", layout="wide")

@st.cache_resource
def get_engine():
    return sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})

# ─── OPTIMIZED DATA FETCHERS (with Caching) ──────────────────────────────────

@st.cache_data(ttl=3600)
def get_cached_global_filters():
    engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
    try:
        # Use summary table for min/max years (MUCH faster)
        years = pd.read_sql("SELECT MIN(year) as min_y, MAX(year) as max_y FROM patent_yearly_summary", engine)
        # Use summary table for countries and cpcs
        countries = pd.read_sql("SELECT DISTINCT country FROM patent_yearly_summary WHERE country IS NOT NULL AND country != ''", engine)
        cpcs = pd.read_sql("SELECT DISTINCT cpc_section FROM patent_yearly_summary WHERE cpc_section IS NOT NULL AND cpc_section != ''", engine)

        min_y = int(years['min_y'].iloc[0]) if pd.notna(years['min_y'].iloc[0]) else 2000
        max_y = int(years['max_y'].iloc[0]) if pd.notna(years['max_y'].iloc[0]) else 2024

        return min_y, max_y, sorted(countries['country'].tolist()), sorted(cpcs['cpc_section'].tolist())
    except Exception:
        return 2000, 2024, [], []

@st.cache_data(ttl=3600)
def get_cached_db_stats():
    engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
    try:
        stats = {}
        # Simple counts are usually indexed
        stats['patents'] = pd.read_sql("SELECT COUNT(*) as c FROM patents", engine)['c'].iloc[0]
        stats['inventors'] = pd.read_sql("SELECT COUNT(*) as c FROM inventors", engine)['c'].iloc[0]
        stats['companies'] = pd.read_sql("SELECT COUNT(*) as c FROM companies", engine)['c'].iloc[0]
        return stats
    except Exception:
        return {'patents': 0, 'inventors': 0, 'companies': 0}

@st.cache_data(ttl=3600)
def fetch_analytics(func_name, *args, **kwargs):
    engine = get_engine()
    func = getattr(analyze_db, func_name)
    return func(engine, *args, **kwargs)

# ─── MAIN DASHBOARD ──────────────────────────────────────────────────────────

def main():
    st.title("Global Patent Intelligence Dashboard 📜")
    
    with st.sidebar:
        st.header("Global Filters")
        
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
            
        min_y, max_y, all_countries, all_cpcs = get_cached_global_filters()
        
        if all_countries and all_cpcs:
            year_range = st.slider("Year Range", min_value=min_y, max_value=max_y, value=(min_y, max_y))
            sel_countries = st.multiselect("Inventor Countries", all_countries)
            sel_cpcs = st.multiselect("CPC Sections", all_cpcs)
            
            st.markdown("---")
            st.header("Database Stats")
            stats = get_cached_db_stats()
            st.metric("Total Patents", f"{stats['patents']:,}")
            st.metric("Total Inventors", f"{stats['inventors']:,}")
            st.metric("Total Companies", f"{stats['companies']:,}")
            
            year_start, year_end = year_range
        else:
            st.info("Run pipeline.py first to load data")
            return
            
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "DESCRIPTIVE", "DIAGNOSTIC", "PREDICTIVE", "DEEP LEARNING", "NETWORK"
    ])
    
    # ------------------ TAB 1: DESCRIPTIVE ------------------
    with tab1:
        st.header("Descriptive Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            df_vol = fetch_analytics('get_patent_volume_over_time', year_start, year_end, sel_countries, sel_cpcs)
            if not df_vol.empty:
                st.plotly_chart(px.line(df_vol, x='year', y='count', title="Patent Volume Over Time"), use_container_width=True)
            
            df_geo = fetch_analytics('get_geographic_distribution', year_start, year_end, sel_countries, sel_cpcs)
            if not df_geo.empty:
                st.plotly_chart(px.choropleth(df_geo, locations="country", locationmode="country names", color="count", title="Geographic Distribution"), use_container_width=True)
                
            df_month = fetch_analytics('get_filing_trends_by_month', year_start, year_end, sel_countries, sel_cpcs)
            if not df_month.empty:
                st.plotly_chart(px.line(df_month, x='month', y='count', title="Monthly Filing Trends"), use_container_width=True)
                
        with col2:
            df_cpc = fetch_analytics('get_technology_breakdown', year_start, year_end, sel_countries, sel_cpcs)
            if not df_cpc.empty:
                st.plotly_chart(px.bar(df_cpc, x='count', y='cpc_section', orientation='h', title="Top 10 Technology Sections (CPC)"), use_container_width=True)
                
            df_inv = fetch_analytics('get_top_inventors', 20, year_start, year_end, sel_countries, sel_cpcs)
            if not df_inv.empty:
                st.plotly_chart(px.bar(df_inv, x='count', y='inventor_name', orientation='h', title="Top 20 Inventors"), use_container_width=True)
                
            df_comp = fetch_analytics('get_top_companies', 20, year_start, year_end, sel_countries, sel_cpcs)
            if not df_comp.empty:
                st.plotly_chart(px.bar(df_comp, x='count', y='company_name', orientation='h', title="Top 20 Companies"), use_container_width=True)

        df_uni = fetch_analytics('get_university_vs_corporate', year_start, year_end, sel_countries, sel_cpcs)
        if not df_uni.empty:
            df_pie = df_uni.groupby('type')['count'].sum().reset_index()
            st.plotly_chart(px.pie(df_pie, values='count', names='type', title="Academic vs Corporate Share"), use_container_width=True)

    # ------------------ TAB 2: DIAGNOSTIC ------------------
    with tab2:
        st.header("Diagnostic Analytics")
        col3, col4 = st.columns(2)
        with col3:
            df_ct_heat = fetch_analytics('get_country_technology_heatmap', year_start, year_end, sel_countries, sel_cpcs)
            if not df_ct_heat.empty:
                df_pivot = df_ct_heat.pivot(index='country', columns='cpc_section', values='count').fillna(0)
                st.plotly_chart(px.imshow(df_pivot, title="Country vs Technology Heatmap", aspect="auto"), use_container_width=True)
        with col4:
            df_hhi = fetch_analytics('get_technology_concentration', year_start, year_end, sel_countries, sel_cpcs)
            if not df_hhi.empty:
                st.plotly_chart(px.line(df_hhi, x='year', y='hhi', title="Technology Concentration (HHI)"), use_container_width=True)
            
            df_anom = fetch_analytics('detect_anomalies', year_start, year_end, sel_countries, sel_cpcs)
            if not df_anom.empty:
                fig11 = px.line(df_anom, x='month', y='count', title="Anomaly Detection")
                anoms = df_anom[df_anom['is_anomaly']]
                fig11.add_scatter(x=anoms['month'], y=anoms['count'], mode='markers', marker=dict(color='red'), name='Anomalies')
                st.plotly_chart(fig11, use_container_width=True)

    # ------------------ TAB 3: PREDICTIVE ------------------
    with tab3:
        st.header("Predictive Analytics")
        col5, col6 = st.columns(2)
        with col5:
            df_pred_vol = fetch_analytics('predict_patent_volume', year_start, year_end, sel_countries, sel_cpcs)
            if not df_pred_vol.empty:
                st.plotly_chart(px.line(df_pred_vol, x='year', y='count', color='type', title="Patent Volume Forecast"), use_container_width=True)
        with col6:
            df_pred_tech = fetch_analytics('predict_technology_trends', year_start, year_end, sel_countries, sel_cpcs)
            if not df_pred_tech.empty:
                st.plotly_chart(px.line(df_pred_tech, x='year', y='count', color='cpc_section', title="Technology Trend Forecast"), use_container_width=True)
        
        df_clusters = fetch_analytics('cluster_companies', 5, year_start, year_end, sel_countries, sel_cpcs)
        if not df_clusters.empty:
            df_clusters['cluster'] = df_clusters['cluster'].astype(str)
            st.plotly_chart(px.scatter(df_clusters, x='total', y='growth', color='cluster', hover_name='company_name', title="Company Clustering", size='total'), use_container_width=True)

    # ------------------ TAB 4: DEEP LEARNING ------------------
    with tab4:
        st.header("Deep Learning: Abstract Classification")
        user_abstract = st.text_area("Paste a patent abstract here to predict its CPC section:", height=100)
        if st.button("Predict"):
            if user_abstract:
                try:
                    pred_class, conf = analyze_db.predict_abstract_category(user_abstract)
                    st.success(f"Predicted CPC Section: **{pred_class}** (Confidence: {conf*100:.1f}%)")
                except Exception:
                    st.warning("Model not trained yet.")
                    
        df_cm = fetch_analytics('get_confusion_matrix_data')
        if not df_cm.empty:
            st.plotly_chart(px.imshow(df_cm, text_auto=True, title="Confusion Matrix Heatmap"), use_container_width=True)

    # ------------------ TAB 5: NETWORK ANALYSIS ------------------
    with tab5:
        st.header("Network Analytics")
        st.info("Network visualization is disabled for performance in this view. Use raw data for deep analysis.")

if __name__ == "__main__":
    main()
