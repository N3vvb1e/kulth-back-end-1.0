import json
import os
import shutil
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from imageprocessor.image_processor import run_preprocessing
from .models import Artwork, Note
from django.views.decorators.http import require_http_methods

@csrf_exempt
def manage_artwork(request):
    if request.method == 'POST':
        # Retrieve data from POST request
        id = request.POST.get('id', '').strip()
        artist = request.POST.get('artist')
        title = request.POST.get('title')
        description = request.POST.get('description')
        picture_zones_data = request.POST.get('pictureZones')

        # Parse picture zones data if available
        picture_zones = json.loads(picture_zones_data) if picture_zones_data else []
        images = request.FILES.getlist('images')
        fs = FileSystemStorage(location='images')

        # Determine if a new artwork is created or an existing one is updated
        if id.isdigit():
            artwork, created = Artwork.objects.update_or_create(
                id=int(id),
                defaults={'artist': artist, 'title': title, 'description': description}
            )
        else:
            artwork = Artwork(artist=artist, title=title, description=description)
            artwork.save()
            created = True

        # Process images
        images_dir = os.path.join('images', str(artwork.id))
        os.makedirs(images_dir, exist_ok=True)

        last_image_index_from_directory = 0
        largest_number = 0
        image_filenames_from_directory = os.listdir(images_dir)
        for image_filename_from_directory in image_filenames_from_directory:
            number = int(os.path.splitext(image_filename_from_directory)[0])
            if number > largest_number:
                largest_number = number
        last_image_index_from_directory = largest_number


        image_filenames = []
        for index, image in enumerate(images, start=last_image_index_from_directory + 1):
            filename = f"{index}{os.path.splitext(image.name)[1]}"
            saved_filename = fs.save(os.path.join(str(artwork.id), filename), image)
            image_filenames.append(saved_filename)

        # Process notes
        existing_note_ids = {note.id for note in Note.objects.filter(artwork=artwork)}
        received_note_ids = set()

        for zone in picture_zones:
            note_id = zone.get('id')
            if note_id and note_id.isdigit():
                note_id = int(note_id)
                received_note_ids.add(note_id)
                note_defaults = {
                    'artwork': artwork,
                    'title': zone.get('title', ''),
                    'zone_description': zone['zone_description'],
                    'x': zone['x'],
                    'y': zone['y'],
                    'width': zone['width'],
                    'height': zone['height']
                }
                Note.objects.update_or_create(
                    id=note_id,
                    defaults=note_defaults
                )
            elif not note_id:
                note = Note(
                    artwork=artwork,
                    title=zone.get('title', ''),
                    zone_description=zone['zone_description'],
                    x=zone['x'],
                    y=zone['y'],
                    width=zone['width'],
                    height=zone['height']
                )
                note.save()

        # Cleanup deleted notes
        for note_id in existing_note_ids - received_note_ids:
            Note.objects.filter(id=note_id).delete()

        return JsonResponse({"status": "Artwork added successfully", "images": image_filenames, "created": created}, status=200)

    return JsonResponse({"error": "This method is not allowed"}, status=405)

def calculate_darkness(image_path, x, y):
    """ Calculate the darkness of an image at a given (x, y) position.
        Darkness is calculated as the inverse of the average pixel value at the position (0 is black, 255 is white).
    """
    with Image.open(image_path) as img:
        img = img.convert('L')  # Convert to grayscale
        pixel = np.array(img)[y, x]  # Get the pixel value at (x, y)
        darkness = 255 - pixel  # Inverse of pixel value for darkness
    return darkness

@csrf_exempt
def delete_artwork(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if id.isdigit():
            artwork_id = int(id)
            try:
                artwork = Artwork.objects.get(id=artwork_id)
                artwork.delete()  # This will delete the artwork record

                # Construct the path for the artwork's images directory
                images_dir = os.path.join('images', str(artwork_id))

                # Check if the directory exists and then remove it
                if os.path.exists(images_dir):
                    shutil.rmtree(images_dir)

                return JsonResponse({"status": "success", "message": f"Artwork with ID {artwork_id} and associated images have been deleted."}, status=200)
            except Artwork.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Artwork not found."}, status=404)
        else:
            return JsonResponse({"status": "error", "message": "Invalid ID format."}, status=400)
    return JsonResponse({"status": "error", "message": "This method is not allowed"}, status=405)

def get_artworks(request):
    print('get_artworks')
    artworks = Artwork.objects.prefetch_related('note_set').all()
    data = []
    for artwork in artworks:
        notes = [note.to_dict() for note in artwork.note_set.all()]
        data.append({
            'id': artwork.id,
            'artist': artwork.artist,
            'title': artwork.title,
            'description': artwork.description,
            'notes': notes
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def delete_image(request, file_path):
    print('delete_image')
    base_dir = os.path.abspath('images')
    full_path = os.path.normpath(os.path.join(base_dir, file_path))

    if not full_path.startswith(base_dir):
        return JsonResponse({"error": "Access denied"}, status=403)

    if os.path.exists(full_path) and os.path.isfile(full_path):
        os.remove(full_path)
        return JsonResponse({"status": "success", "message": f"File {file_path} has been deleted."}, status=200)
    else:
        return JsonResponse({"error": "File not found"}, status=404)