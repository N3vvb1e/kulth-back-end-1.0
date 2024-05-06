import datetime
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

def create_feature_model():
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

def load_feature_model():
    base_model = load_model(weights='imagenet')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
    return model

def run_preprocessing():
    pkl_file_path = 'database_features.pkl'
    image_directory = 'images/'
    model = load_model()

    if os.path.exists(pkl_file_path):
        with open(pkl_file_path, 'rb') as f:
            database_features_dict = pickle.load(f)
    else:
        database_features_dict = {}

    # Generate a set of current images including path relative to image_directory
    current_images = set()
    for dirpath, _, filenames in os.walk(image_directory):
        for filename in filenames:
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                rel_dir = os.path.relpath(dirpath, image_directory)
                rel_file = os.path.join(rel_dir, filename)
                current_images.add(rel_file)

    stored_images = set(database_features_dict.keys())

    # Add new images
    new_images = current_images - stored_images
    for img_name in new_images:
        img_path = os.path.join(image_directory, img_name)
        features = extract_features(model, img_path)
        database_features_dict[img_name] = features
        print('adding image', img_name)

    # Remove deleted images
    deleted_images = stored_images - current_images
    for img_name in deleted_images:
        database_features_dict.pop(img_name, None)
        print('remove image', img_name)

    # Save updated features dictionary
    with open(pkl_file_path, 'wb') as f:
        pickle.dump(database_features_dict, f)

global_model = load_model()

def compare_features(feature1, feature2):
    """Calculate the cosine similarity between two feature vectors."""
    similarity = np.dot(feature1, feature2.T) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))
    return similarity

def find_matching_image(database_features, target_feature):
    """Find the most similar image in the database to the target feature."""
    if not database_features:
        return None, 0  # No images to compare against

    similarities = [compare_features(target_feature, db_feature) for db_feature in database_features.values()]
    if not similarities:
        return None, 0  # No valid similarities found

    max_similarity_index = np.argmax(similarities)
    max_similarity = similarities[max_similarity_index]
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

