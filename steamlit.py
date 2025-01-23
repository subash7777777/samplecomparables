import streamlit as st
import pandas as pd


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
    uploaded_file = st.file_uploader("Upload your hotel data (CSV)", type="csv")

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


if __name__ == "__main__":
    main()
