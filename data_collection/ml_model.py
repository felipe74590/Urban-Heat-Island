import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error


def train_model(data: dict):
    """
    Train a linear regression model using the collected LST, land use, and vegetation indices data.

    Args:
        data (dict): Dictionary containing 'LST', 'land_use', 'vegetation' keys.

    Returns:
        model (LinearRegression): Trained linear regression model.
        metrics (dict): Dictionary with 'MSE' and 'R2' metrics.
    """

    # Extract the input features and target variable
    try:
        lst_data = data.get("LST")
        land_use_data = data.get("Land_Use")
        vegetation_data = data.get("Vegetation")

        if not all([lst_data, land_use_data, vegetation_data]):
            raise ValueError("Missing data. Ensure LST, Land_Use, and Vegetation data are included.")

        # Preparing the features (X) and target (y)
        # For simplicity, using mode for land use and mean values for NDVI/EVI as a single feature set

        land_use = land_use_data.getInfo().get("LC_Type1")
        ndvi = vegetation_data[1].getInfo().get("NDVI")
        evi = vegetation_data[1].getInfo().get("EVI")

        # Constructing the features matrix and target array
        X = pd.DataFrame({"Land_Use": [land_use], "NDVI": [ndvi], "EVI": [evi]})
        y = [lst_data.getInfo()]

        # Split the data into training and test sets (Using all as training in this case for limited data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize and train the model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions and calculate metrics
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        metrics = {"MSE": mse, "R2": r2}
        print(f"Model Metrics: MSE = {mse}, R2 Score = {r2}")

        return model, metrics

    except Exception as e:
        raise RuntimeError(f"Error training model: {str(e)}")
