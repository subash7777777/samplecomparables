import streamlit as st
import pandas as pd
import io

def find_comparables(subject_property, dataset):
    """
    Finds the 5 most comparable properties for the given subject property,
    ensuring the VPR value is within the specified range and all conditions are strictly met.
    """
    # Filter based on conditions
    filtered_df = dataset[
        (dataset['Hotel Name'] != subject_property['Hotel Name']) &
        (dataset['Property Address'] != subject_property['Property Address']) &
        (dataset['Owner Name/ LLC Name'] != subject_property['Owner Name/ LLC Name']) &
        (dataset['Owner Street Address'] != subject_property['Owner Street Address']) &
        (dataset['Hotel Class'] == subject_property['Hotel Class']) &
        (dataset['Type'] == 'Hotel') &
        (dataset['Market Value-2024'] >= subject_property['Market Value-2024'] - 100000) &
        (dataset['Market Value-2024'] <= subject_property['Market Value-2024'] + 100000) &
        # VPR condition: between 50% and 100% of subject property's VPR (inclusive)
        (dataset['VPR'] >= subject_property['VPR'] / 2) & 
        (dataset['VPR'] <= subject_property['VPR']) 
    ].copy()

    # If no properties match the criteria, return an empty DataFrame
    if filtered_df.empty:
        return pd.DataFrame()

    # Calculate differences
    filtered_df['Market_Value_Diff'] = abs(filtered_df['Market Value-2024'] - subject_property['Market Value-2024'])
    filtered_df['VPU_VPR_Diff'] = abs(filtered_df['VPR'] - subject_property['VPR'])

    # Sort and get the top 5
    filtered_df = filtered_df.sort_values(by=['Market_Value_Diff', 'VPU_VPR_Diff']).head(5)
    return filtered_df

def main():
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    /* Custom Color Palette */
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --background-color: #ecf0f1;
        --text-color: #2c3e50;
        --card-background: #ffffff;
    }

    /* Global Styles */
    .main {
        background-color: var(--background-color);
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    }

    /* Title Styling */
    .title {
        color: var(--primary-color);
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5rem;
        letter-spacing: -1px;
    }

    /* Card Styling */
    .stCard {
        background-color: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Button Styling */
    .stButton>button {
        background-color: var(--secondary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: var(--primary-color);
        transform: scale(1.05);
    }

    /* DataFrame Styling */
    .dataframe {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .dataframe th {
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
        padding: 12px;
        text-align: left;
    }

    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
    }

    /* File Uploader Styling */
    .stFileUploader {
        margin-bottom: 20px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Custom Title with Markdown for better styling
    st.markdown('<h1 class="title"> Comparables Analysis</h1>', unsafe_allow_html=True)

    # File upload with custom styling
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Your Dataset", type="csv", help="Please upload a CSV file with property details")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        # Load data
        data = pd.read_csv(uploaded_file)

        # Initialize session state for tracking property index
        if "current_index" not in st.session_state:
            st.session_state.current_index = 0

        # Navigation and Display Container
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            prev_button = st.button("⬅️ Previous", use_container_width=True)
            if prev_button and st.session_state.current_index > 0:
                st.session_state.current_index -= 1
        
        with col3:
            next_button = st.button("➡️ Next", use_container_width=True)
            if next_button and st.session_state.current_index < len(data) - 1:
                st.session_state.current_index += 1

        # Select subject property based on current index
        subject_index = st.session_state.current_index
        subject_property = data.iloc[subject_index]

        # Display subject property
        st.subheader(f"🏘️ Subject Property (Index: {subject_index})")
        st.dataframe(
            subject_property.to_frame().T, 
            use_container_width=True
        )

        # Find comparables
        comparables = find_comparables(subject_property, data)

        # Display comparables
        st.subheader("🔍 Comparable Properties:")
        if not comparables.empty:
            st.dataframe(
                comparables, 
                use_container_width=True
            )
        else:
            st.warning("No comparable properties found based on the given criteria.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Download button with enhanced styling
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        if st.button("📥 Download Comprehensive Results", use_container_width=True):
            # [Previous download logic remains the same]
            results_list = []
            
            for subject_index in range(len(data)):
                try:
                    subject_property = data.iloc[subject_index]
                    comparables = find_comparables(subject_property, data)
                    
                    result_entry = {
                        'VPR': subject_property['VPR'] if 'VPR' in data.columns else None,
                        'Hotel Name': subject_property['Hotel Name'] if 'Hotel Name' in data.columns else None,
                        'Property Address': subject_property['Property Address'] if 'Property Address' in data.columns else None,
                        'Market Value-2024': subject_property['Market Value-2024'] if 'Market Value-2024' in data.columns else None,
                        'Hotel Class': subject_property['Hotel Class'] if 'Hotel Class' in data.columns else None,
                        'Owner Name/ LLC Name': subject_property['Owner Name/ LLC Name'] if 'Owner Name/ LLC Name' in data.columns else None,
                        'Owner Street Address': subject_property['Owner Street Address'] if 'Owner Street Address' in data.columns else None,
                        'Type': subject_property['Type'] if 'Type' in data.columns else None,
                        'account number': subject_property['account number'] if 'account number' in data.columns else None
                    }
                    
                    for i in range(5):
                        prefix = f'comp{i+1} '
                        if i < len(comparables):
                            comp = comparables.iloc[i]
                            result_entry[prefix + 'VPR'] = comp['VPR'] if 'VPR' in comparables.columns else None
                            result_entry[prefix + 'Hotel Name'] = comp['Hotel Name'] if 'Hotel Name' in comparables.columns else None
                            result_entry[prefix + 'Property Address'] = comp['Property Address'] if 'Property Address' in comparables.columns else None
                            result_entry[prefix + 'Market Value-2024'] = comp['Market Value-2024'] if 'Market Value-2024' in comparables.columns else None
                            result_entry[prefix + 'Hotel Class'] = comp['Hotel Class'] if 'Hotel Class' in comparables.columns else None
                            result_entry[prefix + 'Owner Name/ LLC Name'] = comp['Owner Name/ LLC Name'] if 'Owner Name/ LLC Name' in comparables.columns else None
                            result_entry[prefix + 'Owner Street Address'] = comp['Owner Street Address'] if 'Owner Street Address' in comparables.columns else None
                            result_entry[prefix + 'Type'] = comp['Type'] if 'Type' in comparables.columns else None
                            result_entry[prefix + 'account number'] = comp['account number'] if 'account number' in comparables.columns else None
                        else:
                            result_entry[prefix + 'VPR'] = None
                            result_entry[prefix + 'Hotel Name'] = None
                            result_entry[prefix + 'Property Address'] = None
                            result_entry[prefix + 'Market Value-2024'] = None
                            result_entry[prefix + 'Hotel Class'] = None
                            result_entry[prefix + 'Owner Name/ LLC Name'] = None
                            result_entry[prefix + 'Owner Street Address'] = None
                            result_entry[prefix + 'Type'] = None
                            result_entry[prefix + 'account number'] = None
                    
                    results_list.append(result_entry)
                except Exception as e:
                    st.error(f"Error processing row {subject_index}: {e}")
                    continue
            
            result_df = pd.DataFrame(results_list)
            output = io.BytesIO()
            result_df.to_excel(output, index=False, sheet_name='Results', engine='openpyxl')
            
            st.download_button(
                "📄 Download Comprehensive Excel Report",
                data=output.getvalue(),
                file_name='comprehensive_property_comparables.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
