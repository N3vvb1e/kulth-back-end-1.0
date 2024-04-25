from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

import numpy as np
import requests

from artwork.models import Artwork
from artwork.views import get_artwork_by_id
from .forms import ImageUploadForm
from .image_processor import process_uploaded_image
import os
from .ai import generate_response
from django.core import serializers



                    

def upload_image(request):
    similarity_threshold = 0.5

    # Retrieve all artworks from the database
    artwork = get_artwork_by_id()

    additional_data = {
        # "positions": [{"x": 1, "y": 1, "text": "Number 10"}],  # Add more positions as needed
        "positions": [{"x": note.x, "y": note.y, "text": note.zone_description} for note in artwork.note_set.all()],
        "description": artwork.description,
        "title": artwork.title
    }

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES['image']
            matching_image_path, similarity = process_uploaded_image(img)

            similarity = float(similarity.item()) if isinstance(similarity, np.generic) or isinstance(similarity, np.ndarray) else float(similarity)

            if similarity < similarity_threshold:
                return JsonResponse({'message': 'No matching image found', 'similarity': similarity})

            image_name = os.path.basename(matching_image_path)

            return JsonResponse({
                'similarity': similarity,
                'image_name': image_name,
                **additional_data
            })

    else:
        return JsonResponse({'error': 'Invalid method or form data'})


def fetch_image(request, image_name):
    print("fetch_image")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_folder = os.path.join(base_dir, 'images')
    image_path = os.path.join(images_folder, image_name)

    try:
        with open(image_path, "rb") as image_file:
            print('image_path', image_path)
            return HttpResponse(image_file.read(), content_type="image/jpeg")
    except FileNotFoundError:
        return JsonResponse({'error': 'Image not found'}, status=404)
    
def google_text_to_speech(request):
    api_key = "AIzaSyAkXaO7IPCDJ-Shw_-ZNpw8rrWVB95iHfE"
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}


    data = {
        "input": {"text": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."},
        "voice": {"languageCode": "en-US", "name": "en-US-Wavenet-F"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    """
    data = {
        "input": {"text": additional_data["description"]},
        "voice": {"languageCode": "en-US", "name": "ro-RO-Wavenet-A"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    """
    
    response = requests.post(url, headers=headers, json=data)
    audio_content = response.json().get('audioContent', None)

    if audio_content:
        return JsonResponse({"audioContent": audio_content})
    else:
        return JsonResponse({"error": "Failed to generate speech"}, status=500)

def generate_text_using_ai(request):
    # Assuming generate_response returns a non-dict object like a string
    response_data = "asdfs"#generate_response("Tell me a fun fact")
    return JsonResponse({"message": response_data}, safe=True)


def csrf_token(request):
    from django.middleware.csrf import get_token
    return JsonResponse({'csrfToken': get_token(request)})