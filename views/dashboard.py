import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import get_detections, get_counter_history
import time

def dashboard():
    # ================= DARK THEME STYLING =================
    st.markdown("""
        <style>
        /* Hide default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Dark background with network image */
        .stApp {
            background-image: url('https://i.ibb.co/8DQ3y517/image.png') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }
        
        /* Dark overlay */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(13, 25, 35, 0.85);
            z-index: 0;
            pointer-events: none;
        }
        
        /* Content above overlay */
        .main .block-container {
            position: relative;
            z-index: 1;
        }
        
        /* Custom title */
        .dashboard-title {
            text-align: center;
            font-weight: 800;
            font-size: 48px;
            color: #00bcd4;
            text-shadow: 0 0 30px rgba(0, 188, 212, 0.6);
            margin-bottom: 2rem;
            letter-spacing: 1px;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 36px !important;
            color: #00bcd4 !important;
            font-weight: 700 !important;
            text-shadow: 0 0 15px rgba(0, 188, 212, 0.5);
        }
        
        [data-testid="stMetricLabel"] {
            color: #80deea !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            letter-spacing: 2px;
        }
        
        /* Metric containers */
        [data-testid="metric-container"] {
            background: rgba(20, 35, 50, 0.8) !important;
            backdrop-filter: blur(15px);
            padding: 1.5rem !important;
            border-radius: 15px !important;
            border: 1px solid rgba(0, 188, 212, 0.3) !important;
            box-shadow: 
                0 4px 20px rgba(0, 0, 0, 0.3),
                0 0 40px rgba(0, 188, 212, 0.1) !important;
        }
        
        /* Divider */
        hr {
            border: none !important;
            border-top: 2px solid rgba(0, 188, 212, 0.3) !important;
            margin: 2rem 0 !important;
            box-shadow: 0 0 10px rgba(0, 188, 212, 0.2);
        }
        
        /* Warning/Info boxes */
        .stAlert {
            background: rgba(20, 35, 50, 0.9) !important;
            backdrop-filter: blur(10px);
            border-radius: 10px !important;
            border-left: 4px solid #00bcd4 !important;
            color: #b2ebf2 !important;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(0, 188, 212, 0.2) !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #e0f7fa !important;
        }
        
        /* Plot containers */
        .js-plotly-plot {
            border-radius: 15px;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    # ================= TITLE =================
    st.markdown(
        """
        <h1 class="dashboard-title">
             Crowd Monitoring Dashboard
        </h1>
        """,
        unsafe_allow_html=True
    )

    # ================= LOAD DATA =================
    st.cache_data.clear()
    detections = get_detections()
    history = get_counter_history()
    history = history.sort_values(by="timestamp")
    latest = history.iloc[-1]
    
    
    if history.empty:
        st.warning(" No data available yet. Start monitoring to see live statistics.")
        return

    latest = history.iloc[-1]

    # ================= METRICS =================
    col1, col2, col3 = st.columns(3)
    col1.metric("ENTERED", int(latest["entered"]))
    col2.metric("EXITED", int(latest["exited"]))
    col3.metric("INSIDE", int(latest["inside"]))

    st.markdown("---")

    # ================= ROW 1 =================
    row1_col1, row1_col2 = st.columns(2)

    # -------- BAR GRAPH --------
    with row1_col1:
        bar_df = {
            "Type": ["Entered", "Exited", "Inside"],
            "Count": [
                latest["entered"],
                latest["exited"],
                latest["inside"]
            ]
        }

        fig_bar = px.bar(
            bar_df,
            x="Type",
            y="Count",
            color="Type",
            color_discrete_map={
                "Entered": "#00e676",
                "Exited": "#ff5252",
                "Inside": "#00bcd4"
            },
            title="<b>Current Crowd Status</b>",
            text_auto=True
        )

        fig_bar.update_layout(
            title_x=0.5,
            font=dict(size=14, color="#e0f7fa"),
            plot_bgcolor="rgba(20, 35, 50, 0.6)",
            paper_bgcolor="rgba(20, 35, 50, 0.8)",
            title_font=dict(size=18, color="#00bcd4"),
            showlegend=False,
            xaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea"
            ),
            yaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea"
            ),
            margin=dict(l=10, r=10, t=50, b=10)
        )

        fig_bar.update_traces(
            marker=dict(
                line=dict(color="rgba(0, 188, 212, 0.5)", width=2)
            ),
            textfont=dict(size=14, color="white")
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # -------- LINE GRAPH --------
    with row1_col2:
        fig_line = px.line(
            history,
            x="timestamp",
            y="inside",
            title="<b>Crowd Growth Trend Over Time</b>",
            markers=True
        )

        fig_line.update_traces(
            line=dict(color="#00bcd4", width=3),
            marker=dict(
                size=8,
                color="#00e5ff",
                line=dict(color="#00bcd4", width=2)
            )
        )

        fig_line.update_layout(
            title_x=0.5,
            xaxis_title="Time",
            yaxis_title="People Inside",
            font=dict(size=14, color="#e0f7fa"),
            plot_bgcolor="rgba(20, 35, 50, 0.6)",
            paper_bgcolor="rgba(20, 35, 50, 0.8)",
            title_font=dict(size=18, color="#00bcd4"),
            xaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea"
            ),
            yaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea"
            ),
            margin=dict(l=10, r=10, t=50, b=10)
        )

        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # ================= ROW 2 =================
    row2_col1, row2_col2 = st.columns(2)

    # -------- HEATMAP --------
    with row2_col1:
        if detections.empty:
            st.info(" Heatmap will appear once detections are available")
        else:
            fig_heat = px.density_heatmap(
                detections,
                x="x",
                y="y",
                nbinsx=60,
                nbinsy=60,
                color_continuous_scale=[
                    [0, "#0d1929"],
                    [0.2, "#1a3a52"],
                    [0.4, "#00bcd4"],
                    [0.6, "#00e5ff"],
                    [0.8, "#64ffda"],
                    [1, "#00ff88"]
                ],
                title="<b>People Density & Movement Heatmap</b>"
            )

            fig_heat.update_layout(
                title_x=0.5,
                font=dict(size=14, color="#e0f7fa"),
                plot_bgcolor="rgba(20, 35, 50, 0.6)",
                paper_bgcolor="rgba(20, 35, 50, 0.8)",
                title_font=dict(size=18, color="#00bcd4"),
                xaxis=dict(
                    gridcolor="rgba(0, 188, 212, 0.1)",
                    color="#80deea"
                ),
                yaxis=dict(
                    gridcolor="rgba(0, 188, 212, 0.1)",
                    color="#80deea"
                ),
                coloraxis_colorbar=dict(
                    title=dict(text="Density", font=dict(color="#00bcd4")),
                    tickfont=dict(color="#80deea")
                ),
                margin=dict(l=10, r=10, t=50, b=10)
            )

            st.plotly_chart(fig_heat, use_container_width=True)

    # -------- FLOW BALANCE --------
    with row2_col2:
        history["flow_balance"] = history["entered"] - history["exited"]

        fig_area = px.area(
            history,
            x="timestamp",
            y="flow_balance",
            title="<b>Net Crowd Flow Balance</b>",
            labels={
                "timestamp": "Time",
                "flow_balance": "Net Flow (+In / −Out)"
            }
        )

        fig_area.update_traces(
            line=dict(color="#00bcd4", width=2),
            fillcolor="rgba(0, 188, 212, 0.3)"
        )

        fig_area.update_layout(
            title_x=0.5,
            xaxis_title="Time",
            yaxis_title="Net People Flow",
            font=dict(size=14, color="#e0f7fa"),
            plot_bgcolor="rgba(20, 35, 50, 0.6)",
            paper_bgcolor="rgba(20, 35, 50, 0.8)",
            title_font=dict(size=18, color="#00bcd4"),
            xaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea"
            ),
            yaxis=dict(
                gridcolor="rgba(0, 188, 212, 0.1)",
                color="#80deea",
                zeroline=True,
                zerolinecolor="rgba(0, 188, 212, 0.4)",
                zerolinewidth=2
            ),
            margin=dict(l=10, r=10, t=50, b=10)
        )

        st.plotly_chart(fig_area, use_container_width=True)