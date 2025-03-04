import os
import pandas as pd

def read_feedback_data(feedback_directory, condition):
    """
    Reads all feedback-related CSV files from the given directory and assigns a Condition.
    
    Args:
        feedback_directory (str): Path to the feedback directory.
        condition (str): Condition to assign to the feedback data (e.g., 'I', 'R', 'T').
    
    Returns:
        pd.DataFrame: DataFrame containing all feedback data with Condition.
    """
    feedback_dataframes = []
    
    print("Feedback directory_path", feedback_directory)
    for root, _, files in os.walk(feedback_directory):
        print(f"Searching in directory: {root}")
        
        for file in files:
            print("file", file)
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print("file_path", file_path)
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path, encoding='utf-8')
                    
                    # Ensure the required columns are present
                    required_columns = ['Participant Id', 'NASA TLX Score']
                    for col in required_columns:
                        if col not in df.columns:
                            # Add missing columns with default values
                            df[col] = None
                    
                    # Add the Condition column
                    df['Condition'] = condition
                    
                    # Add a column for the source file path (optional)
                    df['Source File'] = file_path
                    
                    feedback_dataframes.append(df)
                    print(f"Successfully read feedback file: {file_path}")
                except Exception as e:
                    print(f"Error reading feedback file {file_path}: {e}")
    
    if not feedback_dataframes:
        print("No feedback CSV files found or all files failed to read.")
        return None
    
    # Concatenate all feedback DataFrames into a single DataFrame
    feedback_df = pd.concat(feedback_dataframes, ignore_index=True)
    
    return feedback_df

def add_feedback_to_merged_data(merged_df, feedback_df, condition):
    """
    Adds NASA TLX scores from feedback data to all rows with the specified Condition.
    
    Args:
        merged_df (pd.DataFrame): The merged DataFrame containing task and feedback data.
        feedback_df (pd.DataFrame): DataFrame containing feedback data with NASA TLX scores.
        condition (str): Condition to match (e.g., 'I', 'R', 'T').
    
    Returns:
        pd.DataFrame: Updated DataFrame with NASA TLX scores added.
    """
    if feedback_df is None:
        print("No feedback data to add.")
        return merged_df
    
    # Filter feedback data for the specified condition
    feedback_df_filtered = feedback_df[feedback_df['Condition'] == condition]
    
    # Get the NASA TLX Score for the condition (use the first value if multiple exist)
    nasa_tlx_score = feedback_df_filtered['NASA TLX Score'].iloc[0] if not feedback_df_filtered.empty else None
    
    # Add the NASA TLX Score to all rows with the specified condition
    if nasa_tlx_score is not None:
        merged_df.loc[merged_df['Condition'] == condition, 'NASA TLX Score'] = nasa_tlx_score
    
    return merged_df

if __name__ == "__main__":
    # Define the directory paths for the feedback CSV files
    feedback_directories = {
        'I': '../data/Feedback/Interruptions',  # Condition: I
        'R': '../data/Feedback/Rest',           # Condition: R
        'T': '../data/Feedback/TimeConstraint', # Condition: T
    }
    
    # Define the path to the existing merged dataset CSV
    merged_dataset_path = 'merged_feature_dataset_PRCD-45BFF9.csv'  # Path to the merged dataset CSV
    
    # Read the existing merged dataset
    try:
        merged_df = pd.read_csv(merged_dataset_path, encoding='utf-8')
        print("Successfully read merged dataset.")
    except Exception as e:
        print(f"Error reading merged dataset: {e}")
        exit()
    
    # Read and add feedback data for each condition
    for condition, feedback_directory in feedback_directories.items():
        print(f"\nProcessing feedback data for Condition: {condition}")
        feedback_data = read_feedback_data(feedback_directory, condition)
        
        if feedback_data is not None:
            # Add NASA TLX scores to the merged dataset
            merged_df = add_feedback_to_merged_data(merged_df, feedback_data, condition)
    
    # Define the output path for the updated merged dataset
    output_path = 'updated_merged_feature_dataset.csv'
    
    # Save the updated merged DataFrame to a new CSV file
    merged_df.to_csv(output_path, index=False, encoding="utf-8")
    
    # Display a message indicating successful creation
    print(f"\nUpdated merged dataset created and saved to {output_path}")