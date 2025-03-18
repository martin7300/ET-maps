# Synthetic Survey Data Accuracy Visualization

This Streamlit application visualises the accuracy of synthetic survey responses compared to real human responses across 160+ countries. It allows users to compare two different approaches - Electric Twin and Baseline - for generating synthetic survey data.

## Features

- Interactive world map showing accuracy scores by country
- Detailed country-level analysis with question-by-question comparisons
- Toggle between Electric Twin and Baseline approaches
- Comprehensive FAQ section explaining the methodology

## Data

The application uses three CSV files that should be placed in a `data` folder:

- `delta_sjsd.csv`: Contains overall accuracy scores by country
- `per_question_sjsd_baseline.csv`: Contains question-level accuracy scores for the Baseline approach
- `per_question_sjsd_electric twin.csv`: Contains question-level accuracy scores for the Electric Twin approach

## Setup & Running Locally

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Place your CSV data files in the `data` directory
4. Run the app:
   ```
   streamlit run app.py
   ```

## Deployment

This app is deployed on Streamlit Community Cloud. Visit [the deployed app](https://et-maps.streamlit.app/) to see it in action.

## About the Data

The application compares synthetic survey responses to data from the Gallup World Poll, covering topics relevant to international security and societal attitudes including:

- Confidence in military, elections, and judicial systems
- Corruption in government
- Approval of various country leaderships
- Attitudes towards minorities
- Freedom of media

## License

© 2025 All rights reserved.
