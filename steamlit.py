import streamlit as st
import pandas as pd
import io

def find_comparables(subject_property, dataset):
    """
    Finds the 5 most comparable properties for the given subject property,
    ensuring the VPR value is within the specified range and all conditions are strictly met.

    Args:
        subject_property: A pandas Series representing the subject property.
        dataset: The pandas DataFrame containing all properties.

    Returns:
        A DataFrame with the 5 most comparable properties.
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
    filtered_df['Combined_Diff'] = filtered_df['Market_Value_Diff'] + filtered_df['VPU_VPR_Diff']

    # Sort and get the top 5
    filtered_df = filtered_df.sort_values(by=['Combined_Diff', 'Market_Value_Diff', 'VPU_VPR_Diff']).head(5)

    return filtered_df


def main():
    # Apply custom styles
    st.markdown(
        """
        <style>
        .main { background-color: #f7f9fc; }
        .stButton>button { background-color: #007bff; color: white; border-radius: 5px; }
        .stButton>button:hover { background-color: #0056b3; }
        h1 { color: #004085; }
        .dataframe { background-color: #ffffff; border-radius: 10px; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Comparable Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload your data (CSV)", type="csv")

    if uploaded_file is not None:
        # Load data
        data = pd.read_csv(uploaded_file)

        # Initialize session state for tracking property index
        if "current_index" not in st.session_state:
            st.session_state.current_index = 0

        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous") and st.session_state.current_index > 0:
                st.session_state.current_index -= 1
        with col2:
            if st.button("Next") and st.session_state.current_index < len(data) - 1:
                st.session_state.current_index += 1

        # Select subject property based on current index
        subject_index = st.session_state.current_index
        subject_property = data.iloc[subject_index]

        # Display subject property
        st.subheader(f"Subject Property (Index: {subject_index})")
        st.dataframe(subject_property.to_frame().T.style.set_properties(**{'background-color': '#eaf4fc', 'border': '1px solid #007bff'}))

        # Find comparables
        comparables = find_comparables(subject_property, data)

        # Display comparables
        st.subheader("Comparable Properties:")
        if not comparables.empty:
            st.dataframe(
                comparables.style.set_properties(
                    **{'background-color': '#ffffff', 'color': '#333', 'border': '1px solid #dddddd'}
                )
            )
        else:
            st.write("No comparable properties found based on the given criteria.")

if st.button("Download Results"):
    # Initialize a list to store rows for the final Excel output
    final_data = []

    # Iterate through each property in the dataset
    for index, subject_property in data.iterrows():
        # Find comparables for the current subject property
        comparables = find_comparables(subject_property, data)

        # Prepare a single row with subject property details and up to 5 comparables
        row = [
            subject_property['VPR'],
            subject_property['Hotel Name'],
            subject_property['Property Address'],
            subject_property['Market Value-2024'],
            subject_property['Hotel Class'],
            subject_property['Owner Name/ LLC Name'],
            subject_property['Owner Street Address'],
            subject_property['Type'],
            subject_property.get('account number', '')  # Handle missing columns gracefully
        ]

        # Add details of up to 5 comparables
        for i in range(5):
            if i < len(comparables):
                comparable = comparables.iloc[i]
                row.extend([
                    comparable['VPR'],
                    comparable['Hotel Name'],
                    comparable['Property Address'],
                    comparable['Market Value-2024'],
                    comparable['Hotel Class'],
                    comparable['Owner Name/ LLC Name'],
                    comparable['Owner Street Address'],
                    comparable['Type'],
                    comparable.get('account number', '')  # Handle missing columns gracefully
                ])
            else:
                # Add empty columns if there are fewer than 5 comparables
                row.extend([''] * 9)

        # Append the row to the final data
        final_data.append(row)

    # Define the column names for the Excel file
    columns = [
        'VPR', 'Hotel Name', 'Property Address', 'Market Value-2024', 'Hotel Class',
        'Owner Name/ LLC Name', 'Owner Street Address', 'Type', 'account number',
        'comp1 VPR', 'comp1 Hotel Name', 'comp1 Property Address', 'comp1 Market Value-2024', 'comp1 Hotel Class',
        'comp1 Owner Name/ LLC Name', 'comp1 Owner Street Address', 'comp1 Type', 'comp1 account number',
        'comp2 VPR', 'comp2 Hotel Name', 'comp2 Property Address', 'comp2 Market Value-2024', 'comp2 Hotel Class',
        'comp2 Owner Name/ LLC Name', 'comp2 Owner Street Address', 'comp2 Type', 'comp2 account number',
        'comp3 VPR', 'comp3 Hotel Name', 'comp3 Property Address', 'comp3 Market Value-2024', 'comp3 Hotel Class',
        'comp3 Owner Name/ LLC Name', 'comp3 Owner Street Address', 'comp3 Type', 'comp3 account number',
        'comp4 VPR', 'comp4 Hotel Name', 'comp4 Property Address', 'comp4 Market Value-2024', 'comp4 Hotel Class',
        'comp4 Owner Name/ LLC Name', 'comp4 Owner Street Address', 'comp4 Type', 'comp4 account number',
        'comp5 VPR', 'comp5 Hotel Name', 'comp5 Property Address', 'comp5 Market Value-2024', 'comp5 Hotel Class',
        'comp5 Owner Name/ LLC Name', 'comp5 Owner Street Address', 'comp5 Type', 'comp5 account number'
    ]

    # Create a DataFrame from the final data
    output_df = pd.DataFrame(final_data, columns=columns)

    # Create an in-memory buffer for the Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        output_df.to_excel(writer, index=False, sheet_name='Comparables')

    # Download the Excel file
    st.download_button(
        "Download Excel",
        data=output.getvalue(),
        file_name='subject_properties_with_comparables.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


if __name__ == "__main__":
    main()
