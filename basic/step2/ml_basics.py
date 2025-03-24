import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

def main():
    # Load the Iris dataset (a classic beginner ML dataset)
    print("Loading Iris dataset...")
    iris = load_iris()
    X = iris.data  # Features
    y = iris.target  # Target variable
    feature_names = iris.feature_names
    target_names = iris.target_names
    
    # Print basic information about the dataset
    print(f"Dataset shape: {X.shape}")
    print(f"Number of classes: {len(target_names)}")
    print(f"Classes: {target_names}")
    print(f"Features: {feature_names}")
    
    # Create a pandas DataFrame for easier data handling
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    df['species'] = df['target'].apply(lambda x: target_names[x])
    
    # Display the first 5 rows of the dataset
    print("\nFirst 5 rows of the dataset:")
    print(df.head())
    
    # Basic data analysis
    print("\nBasic statistics:")
    print(df.describe())
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    print(f"\nTraining set size: {X_train.shape}")
    print(f"Testing set size: {X_test.shape}")
    
    # Standardize the features (important for many ML algorithms)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train a simple K-Nearest Neighbors classifier
    print("\nTraining a K-Nearest Neighbors classifier...")
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train_scaled, y_train)
    
    # Make predictions on the test set
    y_pred = knn.predict(X_test_scaled)
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")
    
    # Print a detailed classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # Make a prediction for a new sample
    new_sample = np.array([[5.1, 3.5, 1.4, 0.2]])  # Example: likely a setosa
    new_sample_scaled = scaler.transform(new_sample)
    prediction = knn.predict(new_sample_scaled)
    predicted_species = target_names[prediction[0]]
    
    print(f"\nPrediction for new sample {new_sample[0]}: {predicted_species}")
    
    # Plot the data for visualization (only using 2 features for simplicity)
    plt.figure(figsize=(10, 6))
    colors = ['blue', 'green', 'red']
    
    for i, species in enumerate(target_names):
        plt.scatter(
            df[df['target'] == i]['sepal length (cm)'],
            df[df['target'] == i]['sepal width (cm)'],
            c=colors[i],
            label=species
        )
    
    plt.xlabel('Sepal Length (cm)')
    plt.ylabel('Sepal Width (cm)')
    plt.title('Iris Dataset: Sepal Length vs Sepal Width')
    plt.legend()
    plt.savefig('iris_visualization.png')
    plt.close()
    print("\nVisualization saved as 'iris_visualization.png'")
    
    return knn, scaler  # Return the trained model and scaler for later use

if __name__ == "__main__":
    main()