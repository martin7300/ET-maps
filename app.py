import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import os

# Set page config
st.set_page_config(
    page_title="Synthetic Survey Data Accuracy",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for Century Gothic font
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Century+Gothic:wght@400;700&display=swap');
    * {font-family: 'Century Gothic', sans-serif;}
    .stExpander {
        border: none !important;
        box-shadow: 0 0 3px rgba(0, 0, 0, 0.1) !important;
        border-radius: 4px !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data():
    # Data directory - using relative path for deployment
    data_dir = "data"
    
    # Load the delta dataset
    delta_df = pd.read_csv(os.path.join(data_dir, "delta_sjsd.csv"))
    
    # Clean country names by removing year patterns
    delta_df['country_clean'] = delta_df['country'].apply(lambda x: re.sub(r'\s*\(\d{4}\)$', '', x))
    
    # Load the per-question datasets
    baseline_df = pd.read_csv(os.path.join(data_dir, "per_question_sjsd_baseline.csv"))
    et_df = pd.read_csv(os.path.join(data_dir, "per_question_sjsd_electric twin.csv"))
    
    # Clean country names in per-question datasets
    baseline_df['Country_clean'] = baseline_df['Country'].apply(lambda x: re.sub(r'\s*\(\d{4}\)$', '', x))
    et_df['Country_clean'] = et_df['Country'].apply(lambda x: re.sub(r'\s*\(\d{4}\)$', '', x))
    
    return delta_df, baseline_df, et_df

# Load data
try:
    delta_df, baseline_df, et_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure all data files are in the 'data' directory.")
    # Create empty dataframes to prevent further errors
    delta_df = pd.DataFrame()
    baseline_df = pd.DataFrame()
    et_df = pd.DataFrame()

# App header
st.title("Synthetic Survey Data Accuracy Visualization")
st.write("Compare accuracy scores between Electric Twin and Baseline approaches across different countries.")

if not delta_df.empty:
    # Create two columns for main layout
    map_col, selection_col = st.columns([3, 1])

    with map_col:
        # Radio button to select approach
        selected_approach = st.radio(
            "Select Approach:",
            ["Electric Twin", "Baseline"],
            horizontal=True
        )
        
        # Function to assign colors based on score
        def get_color(score):
            if score >= 0.95:
                return "#008000"  # Dark green
            elif score >= 0.90:
                return "#90EE90"  # Light green
            elif score >= 0.85:
                return "#FFFF00"  # Yellow
            elif score >= 0.80:
                return "#FF4500"  # Orange red
            else:
                return "#8B0000"  # Dark red
        
        # Create choropleth map with Plotly
        def create_choropleth(selected_approach, delta_df):
            # Determine which column to use
            col_name = 'mean_SJSD_ET' if selected_approach == "Electric Twin" else 'mean_SJSD_Baseline'
            
            # Create a copy of the data for plotting
            plot_data = delta_df.copy()
            
            # Create a color column
            plot_data['color'] = plot_data[col_name].apply(get_color)
            
            # Create a category column for the legend
            def get_category(score):
                if score >= 0.95:
                    return 5  # Dark green
                elif score >= 0.90:
                    return 4  # Light green
                elif score >= 0.85:
                    return 3  # Yellow
                elif score >= 0.80:
                    return 2  # Orange red
                else:
                    return 1  # Dark red
            
            plot_data['category'] = plot_data[col_name].apply(get_category)
            
            # Find min and max for scale
            min_val = min(delta_df[col_name].min(), 0.5)  # Set to 0.5 or lower
            max_val = max(delta_df[col_name].max(), 1.0)  # Ensure it goes to 1.0
            
            # Create figure
            fig = go.Figure()
            
            # Add traces for each category
            for category, color, label in [
                (5, "#008000", ">= 0.95"),  # Dark green
                (4, "#90EE90", "0.90-0.94"),  # Light green
                (3, "#FFFF00", "0.85-0.89"),  # Yellow
                (2, "#FF4500", "0.80-0.84"),  # Orange red
                (1, "#8B0000", "< 0.80")   # Dark red
            ]:
                category_data = plot_data[plot_data['category'] == category]
                
                if len(category_data) > 0:
                    fig.add_trace(go.Choropleth(
                        locations=category_data['country_clean'],
                        z=category_data[col_name],
                        locationmode='country names',
                        colorscale=[[0, color], [1, color]],
                        showscale=False,
                        marker_line_color='white',
                        marker_line_width=0.5,
                        hovertemplate='<b>%{location}</b><br>Accuracy Score: %{z:.4f}<extra></extra>'
                    ))
            
            # Add a dummy trace for the colorbar
            fig.add_trace(go.Choropleth(
                locations=["USA"],  # Dummy location
                z=[min_val],  # Dummy value
                locationmode='country names',
                colorscale=[
                    [0, "#8B0000"],  # Dark red
                    [0.2, "#FF4500"],  # Orange red
                    [0.4, "#FFFF00"],  # Yellow
                    [0.6, "#90EE90"],  # Light green
                    [0.8, "#008000"],  # Dark green
                    [1, "#008000"]  # Dark green
                ],
                showscale=True,
                colorbar=dict(
                    title=dict(
                        text="Accuracy Score",
                        font=dict(family="Century Gothic", size=12)
                    ),
                    tickvals=[min_val, max_val],
                    ticktext=[str(round(min_val, 1)), str(round(max_val, 1))],
                    lenmode="fraction",
                    len=0.6,
                    thickness=15,
                    tickfont=dict(family="Century Gothic", size=10)
                ),
                visible=False  # Hide the dummy trace
            ))
            
            # Update layout
            fig.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)',
                    showcountries=True,
                    countrycolor='white',
                    landcolor='rgba(240, 240, 240, 0.8)'
                ),
                margin=dict(l=0, r=0, t=30, b=0),
                height=550,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Century Gothic")
            )
            
            return fig
        
        # Generate and display the map
        try:
            fig = create_choropleth(selected_approach, delta_df)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating map: {e}")
            st.info("Please try refreshing the page.")

    with selection_col:
        st.subheader("Country Selection")
        st.write("Select a country to view detailed scores:")
        
        # Select a country from dropdown
        selected_country = st.selectbox(
            "",
            options=sorted(delta_df['country_clean'].unique())
        )
        
        # Show average scores
        et_score = delta_df[delta_df['country_clean'] == selected_country]['mean_SJSD_ET'].iloc[0] if not delta_df[delta_df['country_clean'] == selected_country].empty else np.nan
        baseline_score = delta_df[delta_df['country_clean'] == selected_country]['mean_SJSD_Baseline'].iloc[0] if not delta_df[delta_df['country_clean'] == selected_country].empty else np.nan
        
        if not np.isnan(et_score) and not np.isnan(baseline_score):
            st.metric("Electric Twin Score", f"{et_score:.4f}")
            st.metric("Baseline Score", f"{baseline_score:.4f}")
            st.metric("Difference", f"{(et_score - baseline_score):.4f}")

    # Country detail section
    if selected_country:
        st.header(f"Detailed Analysis for {selected_country}")
        
        # Get question-level data for both approaches
        et_data = et_df[et_df['Country_clean'] == selected_country]
        baseline_data = baseline_df[baseline_df['Country_clean'] == selected_country]
        
        if not et_data.empty and not baseline_data.empty:
            st.subheader("Question-level Scores")
            
            # Create combined scores table
            combined_scores = []
            for col in et_data.columns:
                if col not in ['Country', 'Country_clean']:
                    q_name = col.replace('.', ' ')
                    et_score = et_data.iloc[0][col]
                    baseline_score = baseline_data.iloc[0][col]
                    
                    if pd.notna(et_score) and pd.notna(baseline_score) and et_score != 0 and baseline_score != 0:
                        combined_scores.append({
                            'Question': q_name,
                            'Electric Twin': et_score,
                            'Baseline': baseline_score,
                            'Difference': et_score - baseline_score
                        })
            
            # Create a DataFrame and display
            scores_df = pd.DataFrame(combined_scores)
            scores_df = scores_df.sort_values('Electric Twin', ascending=False)
            
            # Format to 4 decimal places
            for col in ['Electric Twin', 'Baseline', 'Difference']:
                scores_df[col] = scores_df[col].round(4)
            
            st.dataframe(scores_df, use_container_width=True)
        else:
            st.write("No question-level data available for this country.")

    # FAQ Section
    st.header("Frequently Asked Questions")

    # What do these maps show?
    with st.expander("What do these maps show?"):
        st.write("""
        The maps visualise the accuracy of two sets of synthetic survey responses compared to the survey responses of real human participants from 140+ countries they aim to mirror. Green colours indicate higher accuracy, whilst yellow and red colours show countries where the synthetic responses differ more significantly from actual human responses.
        """)

    # What survey data was replicated?
    with st.expander("What survey data was replicated?"):
        st.write("""
        The LLM-generated survey datasets replicate questions from the Gallup World Poll (GWP) data, which surveys 1,000-2,000 nationally representative respondents across the globe on various social issues. The topics included in the GWP can be viewed here. We replicated survey responses on questions from the following set of topics looking at issues relevant to international security and wider societal attitudes:
        
        - Confidence in Military
        - Confidence in Honesty of elections
        - Confidence in judicial system
        - Corruption in government
        - Approval of Russia's Leadership
        - Approval of U.K. Leadership
        - Approval of U.S. Leadership
        - Approval of China's Leadership
        - Move Away or Stay
        - Attitudes towards Gay and/or Lesbian People
        - Attitudes towards Racial/Ethnic Minorities
        - Freedom of Media
        """)

    with st.expander("What is the Electric Twin approach?"):
        st.write("""
        Electric Twin is a technology company focused on building science-based synthetic populations and the tools to interact with them. Their synthetic populations are crafted to simulate real-world populations with high fidelity. ET's proprietary approach to building synthetic populations allows users to survey, interview and run focus groups with synthetic samples from all over the world in seconds.
        """)

    with st.expander("What is the baseline approach?"):
        st.markdown("""
        To understand the accuracy of the synthetic responses generated by ET's proprietary approach, we compare the synthetic responses generated by their populations with a baseline approach that is inspired by academic research in the field of synthetic surveying. The baseline approach serves as a transparent line in the sand that ET's engine for building synthetic survey populations can be compared against. The baseline approach works by creating a synthetic persona for each real respondent in the Gallup World Poll (GWP) using the prompt below, and asking GPT-4o-mini to respond to our selected set of survey questions from the GWP:
        
        ```
        It is [YEAR]. You are a [AGE] year-old [GENDER] living in a [URBAN_RURAL] area of [REGION], [COUNTRY]. [You were born in [COUNTRY_BIRTH]].

        You completed [EDUCATION_LEVEL] and currently work in the [PUBLIC/PRIVATE SECTOR], earning [INCOME_LEVEL] per year. You identify as [RELIGIOUS_AFFILIATION]. You are [MARITAL_STATUS] and have [NUMBER_OF_CHILDREN] children.

        You generally have [CONFIDENCE] in your government to do what is right and [APPROVE] of its current performance. 

        Right now, you feel your standard of living is getting [BETTER/WORSE] and think the economic conditions in the city or area where you live, as a whole, are getting [BETTER/WORSE].

        Given this background, please respond to the following survey questions as this person would:

        [EVALUATION_QUESTIONS]
        ```
        """)

    with st.expander("What is an accuracy score?"):
        st.write("""
        Our accuracy score shows how closely our synthetic survey responses mirror real people's answers. When real and synthetic responses are almost identical, the score is close to 1 (shown as darker green on our map). When they're very different, the score approaches 0 (shown as darker red). The metric we use to calculate these scores is "1 minus Jensen-Shannon Divergence" which compares the pattern of answers given by real people with those from our synthetic populations. Think of it as measuring the overlap between two sets of survey results - the more they overlap, the higher the accuracy score and the greener the country appears.
        
        This measurement allows us to see at a glance which approach - Electric Twin or Baseline - better captures what real people in each country actually think about these important issues.
        """)

    # Footer
    st.markdown("---")
    st.write("© 2025 All rights reserved.")
else:
    st.error("No data available. Please check the data files in the data directory.")
