from io import BytesIO
import numpy as np
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.models import Model
import pickle


def load_model():
    base_model = ResNet50(weights='imagenet')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
    return model

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded_dims)

def extract_features(model, img_path):
    preprocessed_image = preprocess_image(img_path)
    features = model.predict(preprocessed_image)
    return features

def run_preprocessing():
    print('run_preprocessing')
    pkl_file_path = 'database_features.pkl'
    
    if not os.path.exists(pkl_file_path):
        model = load_model()
        image_directory = 'images/'
        database_features_dict = {}

        for img_name in os.listdir(image_directory):
            if img_name.endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(image_directory, img_name)
                features = extract_features(model, img_path)
                database_features_dict[img_name] = features

        # Only save the .pkl file if it does not already exist
        with open(pkl_file_path, 'wb') as f:
            pickle.dump(database_features_dict, f)
    else:
        print(".pkl file already exists. Skipping preprocessing.")




global_model = load_model()

def compare_features(feature1, feature2):
    """Calculate the cosine similarity between two feature vectors."""
    similarity = np.dot(feature1, feature2.T) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))
    return similarity

def find_matching_image(database_features, target_feature):
    """Find the most similar image in the database to the target feature."""
    similarities = [compare_features(target_feature, db_feature) for db_feature in database_features.values()]
    max_similarity_index = np.argmax(similarities)
    max_similarity = similarities[max_similarity_index]

    # Retrieve the matching image name using the index
    matching_image_name = list(database_features.keys())[max_similarity_index]
    return matching_image_name, max_similarity


def process_uploaded_image(uploaded_image):
    # Convert the uploaded file to a BytesIO object
    img_stream = BytesIO(uploaded_image.read())
    uploaded_image.seek(0)  # Reset file pointer to the beginning

    # Load the image from BytesIO object
    img = image.load_img(img_stream, target_size=(224, 224))
    
    # Other processing remains the same
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    preprocessed_image = preprocess_input(img_array_expanded_dims)
    
    # Extract features of the uploaded image
    target_features = global_model.predict(preprocessed_image)

    # Load the preprocessed image features
    with open('database_features.pkl', 'rb') as f:
        database_features_dict = pickle.load(f)

    # Find the matching image
    matching_image, similarity = find_matching_image(database_features_dict, target_features)
    
    # Find the name of the matching image
    for img_name, db_features in database_features_dict.items():
        if np.array_equal(db_features, database_features_dict[matching_image]):
            matching_image_name = img_name
            break

    return matching_image_name, similarity

