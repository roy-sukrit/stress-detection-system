import os
import pandas as pd
import uuid

def generate_participant_id():
    unique_participant_id = f"PRCD-{uuid.uuid4().hex[:6].upper()}"
    return unique_participant_id

def merge_csv_files(directory_paths):
    dataframes = []
    
    for directory_path in directory_paths:
        print("directory_path", directory_path)
        for root, _, files in os.walk(directory_path):
            print(f"Searching in directory: {root}")
            
            for file in files:
                print("file", file)
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    print("file_path", file_path)
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8')
                        print(f"Columns in {file_path}: {df.columns.tolist()}")
                        dataframes.append(df)
                        print(f"Successfully read {file_path}")
                        # print(dataframes)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    if not dataframes:
        print("No CSV files found or all files failed to read.")
        return None
    
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    
    
    participant_id = generate_participant_id()
    merged_df['Participant Id'] = participant_id
    
    return merged_df, participant_id

if __name__ == "__main__":
    directory_paths = [
        '/Users/src/Sukrit_Development/stress-analysis/data/Task 1: Word Unscramble Task',
        # "../data/Task 2: Sentence Rephrase Task",
        # "/Users/src/Sukrit_Development/stress-analysis/data/Task 3: Report Writing Task",
        #  "/Users/src/Sukrit_Development/stress-analysis/data/Task 4: Interruptions Task",
        #  "/Users/src/Sukrit_Development/stress-analysis/data/Task 5: Combination Task",
        # "/Users/src/Sukrit_Development/stress-analysis/data/Task 6: Rest Task"
    ]
    
    merged_data, participant_id = merge_csv_files(directory_paths)
    
    if merged_data is not None:
        output_path = f'merged_feature_dataset_{participant_id}.csv'
        print("merged_data ====>",merged_data)
        print("🔍 Checking merged_data before saving...")
        print(merged_data.info())  # Shows if data exists
        merged_data["Event Details"] = merged_data["Event Details"].astype(str).str.replace("\n", " ")
        merged_data = merged_data.fillna("N/A")  # Replace NaN with "N/A"

        print(merged_data.head())  # Shows first few rows
        merged_data.to_csv(output_path, index=False, encoding="utf-8")
        # merged_data.to_csv(output_path, index=False)
        print(f"Feature dataset created and saved to {output_path}")