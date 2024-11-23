# Import the necessary libraries
import pathlib

import hdbscan
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from sklearn.neighbors import KDTree
from sklearn.preprocessing import StandardScaler


def load_data(file_path):
    """
    Load data from an Excel file.

    Parameters:
    - file_path (str): Path to the Excel file.

    Returns:
    - pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    return pd.read_excel(file_path)


def clean_column_names(df):
    """
    Clean column names by removing leading and trailing whitespaces.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with cleaned column names.
    """
    return df.rename(columns=lambda x: x.strip())


def remove_missing_values(df):
    """
    Remove columns with missing values from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with missing values removed.
    """
    return df.dropna(axis=1, how="any", inplace=False)


def preprocess_numerical_features(df):
    """
    Standardize numerical features in the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with numerical features.
    """
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[["Ship Quantity", "Price"]])
    df[["Ship Quantity", "Price"]] = scaled
    df[["Ship Quantity", "Price"]] = df[[
        "Ship Quantity", "Price"]].astype(float)


def convert_to_category(df, columns):
    """
    Convert specified columns to the 'category' data type.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - columns (list): List of columns to be converted.
    """
    df[columns] = df[columns].astype("category")


def encode_categorical_columns(df, columns):
    """
    Encode categorical columns using integer labels.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - columns (list): List of columns to be encoded.
    """
    for column in columns:
        df[column] = df[column].cat.codes


def apply_pca(df):
    """
    Apply Principal Component Analysis (PCA) to the DataFrame and print results.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    """
    pca = PCA()
    pca.fit(df)
    print(df.columns)
    print(pca.explained_variance_ratio_)


def scatter_plot(df, x_column, y_column):
    """
    Create a scatter plot of two columns from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - x_column (str): Name of the x-axis column.
    - y_column (str): Name of the y-axis column.
    """
    plt.scatter(df[x_column], df[y_column])
    plt.show()


def apply_hdbscan(df, min_samples, min_cluster_size_values, cluster_selection_epsilon_values):
    """
    Apply HDBSCAN clustering to the DataFrame with various parameters and display clusters.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - min_samples (list): List of values for the 'min_samples' parameter.
    - min_cluster_size_values (list): List of values for the 'min_cluster_size' parameter.
    - cluster_selection_epsilon_values (list): List of values for the 'cluster_selection_epsilon' parameter.
    """
    for samples in min_samples:
        for min_cluster_size in min_cluster_size_values:
            for epsilon in cluster_selection_epsilon_values:
                hdbscan = HDBSCAN(
                    min_samples=samples,
                    min_cluster_size=min_cluster_size,
                    cluster_selection_epsilon=epsilon
                )
                df["Cluster"] = hdbscan.fit_predict(df)
                display_clusters(df, samples, min_cluster_size, epsilon)


def single_hdbscan(df):
    """
    Apply HDBSCAN clustering to the DataFrame with various parameters and display clusters.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - clusterer: HDBSCAN clustering model fit on the aforementioned df.
    """
    clusterer = hdbscan.HDBSCAN(prediction_data=True)
    clusterer.fit(df)
    return clusterer


def display_clusters(df, samples, min_cluster_size, epsilon):
    """
    Display information about clusters in the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with cluster information.
    - samples (int): Value of 'min_samples' parameter.
    - min_cluster_size (int): Value of 'min_cluster_size' parameter.
    - epsilon (float): Value of 'cluster_selection_epsilon' parameter.
    """
    if not df.loc[df["Cluster"] == -1].empty:
        print(
            f"Min samples: {samples}\nMin Cluster Size: {min_cluster_size}\nCluster Selection Epsilon: {epsilon}")
        print("Number of clusters:", df["Cluster"].nunique(dropna=True))
        print(df.loc[df["Cluster"] == -1].head())
        print("------------------")


def build_kd_tree(df, leaf_size):
    """
    Build a KD-Tree from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - leaf_size (int): Leaf size for the KD-Tree.

    Returns:
    - sklearn.neighbors.KDTree: Built KD-Tree.
    """
    return KDTree(df, leaf_size=leaf_size)


def query_kd_tree(kd_tree, query_point, k):
    """
    Query a KD-Tree with a specific point and return distances and indices.

    Parameters:
    - kd_tree (sklearn.neighbors.KDTree): KD-Tree to be queried.
    - query_point (pd.DataFrame): Query point as a DataFrame.
    - k (int): Number of nearest neighbors to retrieve.

    Returns:
    - tuple: Tuple containing distances and indices of nearest neighbors.
    """
    distances, indices = kd_tree.query(query_point, k=k)
    return distances, indices


def highlight_differences(query_point, neighbor_row, idx):
    """
    Highlight differences between a query point and its neighbor.

    Parameters:
    - query_point (pd.DataFrame): Query point as a DataFrame.
    - neighbor_row (pd.Series): Neighbor row from the DataFrame.
    - idx (int): Index of the neighboring point.
    """
    diff_mask = (query_point != neighbor_row)
    diff_columns = diff_mask.any()

    if diff_columns.any():
        print("Differences:")
        for col in diff_columns[diff_columns].index:
            print(
                f"{col}: Query = {original_df[col].values[0]} || Neighbor = {original_df.loc[idx][col]}"
            )
        print()


def print_results(original_df, query_point, indices, distances, df):
    """
    Print results of querying a KD-Tree with a specific point.

    Parameters:
    - original_df (pd.DataFrame): Original DataFrame.
    - query_point (pd.DataFrame): Query point as a DataFrame.
    - indices (array): Indices of nearest neighbors.
    - distances (array): Distances to nearest neighbors.
    - df (pd.DataFrame): DataFrame containing the queried point and neighbors.
    """
    print(f"Query point\n{query_point}\n")
    print("Nearest neighbors:\n")
    for i, idx in enumerate(indices[0]):
        if not i == 0:
            print(
                f"Neighbor {i}:\n{original_df.loc[idx]}\nDistance: {distances[0][i]}\n"
            )
            highlight_differences(query_point, df.loc[idx], idx)


def create_hybrid_row(df, cluster1, cluster2):
    """
    Creates a new row by combining random rows from two specified clusters.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data.
    - cluster1 (int): The cluster identifier for the first random row selection.
    - cluster2 (int): The cluster identifier for the second random row selection.

    Returns:
    pd.DataFrame: A new row generated by combining values from a random row in cluster1
                  with values from a random row in cluster2. The "Cluster" column is excluded.
    """
    # Select a random row from cluster1
    row1 = df[df["Cluster"] == cluster1].sample(1)

    # Select a random row from cluster2
    row2 = df[df["Cluster"] == cluster2].sample(1)

    # Extract 3 column values from row1
    values_from_row1 = row1.iloc[0, :3].values

    # Extract 4 column values from row2
    values_from_row2 = row2.iloc[0, 3:].values

    # Combine the values to create a new row
    new_row = pd.DataFrame(
        [np.concatenate([values_from_row1, values_from_row2])],
        columns=df.columns
    )
    new_row.drop(columns=["Cluster"], inplace=True)

    return new_row


def add_anomalous_data(df, cluster1):
    """
    Adds anomalous data to the input DataFrame by creating and concatenating hybrid rows.

    Parameters:
    - df (pd.DataFrame): The input DataFrame to which anomalous data will be added.
    - cluster1 (int): The cluster to source half of the columns from.

    Returns:
    pd.DataFrame: A new DataFrame with anomalous data added by concatenating hybrid rows
                  generated from a base row in cluster 0 and different target clusters.
                  The "Cluster" column is excluded.
    """
    new_df = pd.DataFrame(columns=df.columns).drop(
        columns=["Cluster"], inplace=True
    )
    if cluster1 == 0:
        for i in range(1, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 1:
        new_df = pd.concat([new_df, create_hybrid_row(
            df, cluster1, 0)], ignore_index=True)
        for i in range(2, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 2:
        for i in range(2):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(3, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 3:
        for i in range(3):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(4, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 4:
        for i in range(4):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(5, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 5:
        for i in range(5):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(6, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 6:
        for i in range(6):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(7, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 7:
        for i in range(7):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(8, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 8:
        for i in range(8):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
        for i in range(9, 10):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    elif cluster1 == 9:
        for i in range(9):
            new_df = pd.concat([new_df, create_hybrid_row(
                df, cluster1, i)], ignore_index=True)
    new_df = new_df.astype({
        "Product Name": "int32",
        "Ship to Location": "int32",
        "Dealer Name": "int32"
    })
    xlsx_file = pathlib.Path(__file__).parent.parent / 'resources/anomalous_data.xlsx'
    new_df.to_excel(xlsx_file)
    return new_df


def predict_outlier(df, model):
    """
    Predicts outliers in a given DataFrame using a pre-trained clustering model.

    Args:
        df (pd.DataFrame): The input DataFrame containing data for outlier prediction.
        model: The clustering model used for predicting outliers.

    Returns:
        tuple: A tuple containing the following elements:
            - test_labels (numpy.ndarray): Predicted labels for the anomalous data points.
            - strengths (numpy.ndarray): Strength values indicating the degree of outlierness.
            - anomalous_df (pd.DataFrame): DataFrame containing the original data with added 'Cluster' column.

    Note:
        The input DataFrame 'df' is expected to have the same structure as the one used to train the model.
        The clustering model should have a 'labels_' attribute indicating the cluster assignments.

    Example:
        >>> df = pd.DataFrame({'feature1': [1, 2, 3], 'feature2': [4, 5, 6]})
        >>> model = HDBSCAN(min_cluster_size=2).fit(df)
        >>> test_labels, strengths, anomalous_df = predict_outlier(df, model)
    """
    df["Cluster"] = model.labels_
    anomalous_df = pd.DataFrame(columns=df.columns).drop(columns=["Cluster"], inplace=True)

    for i in range(10):
        anomalous_df = pd.concat([anomalous_df, add_anomalous_data(df, i)], ignore_index=True)
        test_labels, strengths = hdbscan.approximate_predict(model, np.unique(anomalous_df, axis=0))

    return test_labels, strengths, anomalous_df


# Main script
if __name__ == "__main__":
    file_path = pathlib.Path(__file__).parent.parent / 'resources/hd-dataset.xlsx'
    df = load_data(file_path)

    df = clean_column_names(df)
    df = remove_missing_values(df)
    original_df = df.copy(deep=True)

    categorical_columns = ["Product Name", "Ship to Location", "Dealer Name"]

    preprocess_numerical_features(df)
    convert_to_category(df, categorical_columns)
    encode_categorical_columns(df, categorical_columns)
    print("Preprocessed data\n", df.head(), "\n\n")

    # Uncomment if you want to apply PCA and scatter plot
    # apply_pca(df)
    # scatter_plot(df, "Ship Quantity", "Product Name")

    # Uncomment to run the HDBSCAN clustering with different argument values
    # min_samples = [5, 6, 7, 8]
    # min_cluster_size_values = [5, 10, 20]
    # cluster_selection_epsilon_values = [0.1, 0.3, 0.5]

    # apply_hdbscan(df, min_samples, min_cluster_size_values, cluster_selection_epsilon_values)

    # Create anomalous data and check it for outliers
    clusterer = single_hdbscan(df)
    test_labels, _, anomalous_df = predict_outlier(df, clusterer)
    print("Potentially anomalous data\n", anomalous_df, "\n\n")
    print("Indices of outliers:", np.where(test_labels == -1)[0], "\n\n")

    # Train a K-D tree on the original data
    leaf_size = 30
    df.drop(columns=["Cluster"], inplace=True)
    kd_tree = build_kd_tree(df.drop_duplicates(), leaf_size)

    # Retrive the closest points to the aforementioned outliers
    for i in np.where(test_labels == -1)[0]:
        query_point = anomalous_df.iloc[i:i + 1]
        distances, indices = query_kd_tree(kd_tree, query_point, k=5)
        print_results(df, query_point, indices, distances, df)
