import json
import logging
import re
import numpy as np
import requests
import os
import environ
from django.http import HttpResponse, JsonResponse
from artwork.models import Artwork
from .forms import ImageUploadForm
from .image_processor import process_uploaded_image
from .ai import generate_response
from django.core import serializers

env = environ.Env()
environ.Env.read_env()
OPENAI_API_KEY = env('OPENAI_API_KEY')
GOOGLE_API_KEY = env('GOOGLE_API_KEY')


      
def upload_image(request):
    similarity_threshold = 0.2 # For production, set it to 0.7
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES['image']
            matching_image_path, similarity = process_uploaded_image(img)
            similarity = float(similarity)

            print('similarity', similarity, "matching_image_path", matching_image_path)
            if similarity < similarity_threshold:
                return JsonResponse({'message': 'No matching image found', 'similarity': similarity})

            artwork_id = extract_artwork_id(matching_image_path)
            print('artwork_id', artwork_id)

            artwork = Artwork.objects.get(id=artwork_id)            

            request.session['artwork_data'] = {
                "pictureZones": [{"x": note.x, "y": note.y, "width": note.width, "height": note.height, "description": note.zone_description, "title": note.title} for note in artwork.note_set.all()],
                "description": artwork.description,
                "title": artwork.title,
            }

            request.session.modified = True

            print('os.path.splitext(matching_image_path)', os.path.splitext(matching_image_path)[1])

            return JsonResponse({
                "pictureZones": [{"x": note.x, "y": note.y, "width": note.width, "height": note.height, "description": note.zone_description, "title": note.title, "darkness": note.darkness} for note in artwork.note_set.all()],
                'title': artwork.title,
                'description': artwork.description,
                'id': artwork.id,
                'first_image_file_extension': os.path.splitext(matching_image_path)[1]
            })

    else:
        return JsonResponse({'error': 'Invalid method or form data'})


def extract_artwork_id(image_path):
    match = re.search(r'(\d+)', image_path)
    if match:
        return int(match.group(1))
    raise ValueError("No valid ID found in the image path")

def remove_extension(filename):
    last_dot_index = filename.rfind('.')
    if last_dot_index != -1:
        return filename[:last_dot_index]
    return filename


def fetch_image(request, image_name):
    print("fetch_image")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_folder = os.path.join(base_dir, 'images')

    # Sanitize the image_name to prevent directory traversal
    image_name = os.path.normpath(image_name)
    if image_name.startswith('..') or os.path.isabs(image_name):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    image_path = os.path.join(images_folder, image_name)
    print('image_path', image_path)

    try:
        with open(image_path, "rb") as image_file:
            return HttpResponse(image_file.read(), content_type="image/jpeg")
    except FileNotFoundError:
        return JsonResponse({'error': 'Image not found'}, status=404)

def google_text_to_speech(request):
    print('google_text_to_speech')

    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": GOOGLE_API_KEY, "Content-Type": "application/json"}

    # Get the pictureZoneIndex from query parameters
    picture_zone_index = request.GET.get('zoneIndex')
    print('picture_zone_index', picture_zone_index)
    if picture_zone_index is not None:
        print("picture_zone_index", picture_zone_index)
        picture_zone_index = int(picture_zone_index)  # Convert index to integer

    picture_data = request.session.get('artwork_data', {})
    print('picture_data: ', picture_data)
    picture_zones = picture_data.get('pictureZones', [])

    # Check if the pictureZoneIndex is valid and set the description
    if picture_zones and picture_zone_index is not None and 0 <= picture_zone_index < len(picture_zones):
        description = picture_zones[picture_zone_index].get('description', '')
    else:
        description = picture_data.get('description', '')  # Fallback to general description

    data = {
        "input": {"text": description},
        "voice": {"languageCode": "en-US", "name": "en-US-Wavenet-F"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    response = requests.post(url, headers=headers, json=data)
    audio_content = response.json().get('audioContent', None)

    if audio_content:
        return JsonResponse({"audioContent": audio_content})
    else:
        return JsonResponse({"error": "Failed to generate speech"}, status=500)

def generate_text_using_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            prompt = data.get('message', '')
            print('prompt', prompt)

            picture_data = request.session.get('artwork_data', {})
            print("picture_data ai: ", picture_data)
            if not picture_data:
                return JsonResponse({"error": "No art data available"}, status=404)

            title = picture_data.get('title', '')
            description = picture_data.get('description', '')
            query = f"Title of the picture: {title} Informations about the painting: {description} Question: {prompt}"

            response_data = generate_response(query)
            print('response_data', response_data)
            if isinstance(response_data, dict):
                return JsonResponse(response_data, safe=False)
            else:
                return JsonResponse({"message": response_data}, safe=True)
        except Exception as e:
            logging.error(f"Failed to process request: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid method"}, status=400)

def csrf_token(request):
    from django.middleware.csrf import get_token
    return JsonResponse({'csrfToken': get_token(request)})