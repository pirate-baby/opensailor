from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from webapp.settings import APP_NAME
from webapp.models import Media

api = NinjaAPI(
    title=f"{APP_NAME} API",
)


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


@api.post("/upload-image")
def upload_image(request, file: UploadedFile = File(...)):
    """Upload image for Milkdown editor and return URL"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401
    
    # Check if file is an image
    if not file.content_type.startswith('image/'):
        return {"error": "Only image files are allowed"}, 400
    
    try:
        # Create Media object
        media = Media(
            uploaded_by=request.user,
            original_filename=file.name,
        )
        media.save()
        
        # Save the uploaded file
        media.file.save(file.name, file, save=True)
        
        return {
            "success": True,
            "url": media.url,
            "id": media.id
        }
    
    except Exception as e:
        return {"error": str(e)}, 500
