from django.shortcuts import render, redirect
from .forms import ArtworkForm
from .models import Artwork
from django.shortcuts import get_object_or_404

# def add_artwork(request):
#     print("add_artwork")
#     if request.method == 'POST':
#         form = ArtworkForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('list_artworks')
#     else:
#         form = ArtworkForm()
#     return render(request, 'artwork/add_artwork.html', {'form': form})

def get_artwork_by_id():
    #artworks = Artwork.objects.all()  # Retrieve all artworks from the database
    #print(artworks)
    #return render(request, 'artwork/list_artworks.html', {'artworks': artworks})
    artwork = get_object_or_404(Artwork, pk=1)
    return artwork
