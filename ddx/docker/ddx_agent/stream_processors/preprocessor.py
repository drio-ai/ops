import pathlib
import pickle

import hdbscan
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KDTree
from scipy.spatial import KDTree


def clean_column_names(df):
    """
    Clean column names by removing leading and trailing whitespaces.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with cleaned column names.
    """
    return df.rename(columns=lambda x: x.strip())


def drop_missing_value_columns(df):
    """
    Remove columns with missing values from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with missing values removed.
    """
    return df.dropna(axis=1, how="all", inplace=False)


def preprocess_numerical_features(df, numerical_features, scale=None):
    """
    Standardize numerical features in the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame with numerical features.
    """
    if scale is not None:
        scaled = scale.transform(df[numerical_features])
    else:
        scale = StandardScaler()
        scaled = scale.fit_transform(df[numerical_features])

    df[numerical_features] = scaled
    df[numerical_features] = df[numerical_features].astype(float)
    return scale


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
    encoded_mappings = {}
    for col in columns:
        encoded_mappings[col] = dict(zip(df[col], df[col].cat.codes))
        df[col] = df[col].cat.codes

    return encoded_mappings


def drop_columns(df, cols):
    """
    Remove id columns from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with missing values removed.
    """
    return df.drop(columns=cols)


def build_kd_tree(df, leaf_size=40):
    """
    Build a KD-Tree from the DataFrame.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.
    - leaf_size (int): Leaf size for the KD-Tree.

    Returns:
    - sklearn.neighbors.KDTree: Built KD-Tree.
    """
    # return KDTree(df, leaf_size=leaf_size)
    return KDTree(df, leafsize=leaf_size)


def query_kd_tree(kd_tree, query_point, k=5):
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


def load_data_from_xlsx(file_path):
    """
    Load data from an Excel file.

    Parameters:
    - file_path (str): Path to the Excel file.

    Returns:
    - pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    return pd.read_excel(file_path)


def first_hdbscan(file_path, subject, discard_columns, categorical_columns, numerical_features):
    df = load_data_from_xlsx(file_path)
    df = clean_column_names(df)
    df = drop_columns(df, discard_columns)
    s = preprocess_numerical_features(df, numerical_features)
    convert_to_category(df, categorical_columns)
    e = encode_categorical_columns(df, categorical_columns)
    cluster = hdbscan.HDBSCAN(prediction_data=True)
    cluster.fit(df)
    kd_tree = build_kd_tree(df.drop_duplicates())
    return {subject: {'model': cluster, 'scale': s, 'encoder': e, 'kd_tree': kd_tree}}


# This will generate the trained model
if __name__ == '__main__':
    file_path = pathlib.Path(__file__).parent.parent / 'resources/hd-dataset.xlsx'
    subject = 'SalesforceOrders'
    discard_columns = ['Order ID', 'Desired ETA']
    categorical_columns = ["Product Name", "Ship to Location", "Dealer Name"]
    numerical_features = ["Ship Quantity", "Price"]
    model = first_hdbscan(file_path, subject, discard_columns, categorical_columns, numerical_features)
    pkl = pathlib.Path(__file__).parent.parent / 'resources/cluster_models.pkl'
    with open(pkl, 'wb') as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
