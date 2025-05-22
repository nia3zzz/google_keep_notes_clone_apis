from rest_framework.decorators import api_view
from ..utils.api_response import APIResponse
from pydantic import ValidationError
from ..validators.note_validators import CreateNoteValidator
from auth_sessions.utils import verifyToken
from users.models import User
import cloudinary.uploader
from notes.models import Notes


# create a note view function that will recieve data from the client process them and save those data in the database including optional images, audio files and video files.
@api_view(["POST"])
def create_note(request):
    # pass the request object to the verify token function which will verify the cookie and return the decoded id incase of successful verification
    decodeToken = verifyToken(request)

    # incase the verification was unsuccesful will return False
    if decodeToken == False:
        return APIResponse(False, 401, "Unauthorized")

    try:
        # geting hold of the user
        found_user = User.objects.get(id=decodeToken)
    except User.DoesNotExist:
        return APIResponse(False, 401, "Unauthorized")

    # hold the form data in a dicionary type variable
    data = {
        "title": request.data.get("title"),
        "note": request.data.get("note"),
        "files": request.FILES.getlist("files"),
        "collaborators": request.data.getlist("collaborators"),
    }

    try:
        # validate the data dictionary using a pydantic validator
        validate_data = CreateNoteValidator(**data)
    except ValidationError as e:
        return APIResponse(False, 400, "Failed in type validation.", error=e.errors())

    try:
        # if the collaborators field is given
        if validate_data.collaborators != None:
            invalid_ids = []

            for collaborator in validate_data.collaborators:
                try:
                    User.objects.get(id=collaborator)
                except User.DoesNotExist:
                    invalid_ids.append(collaborator)

            if invalid_ids:
                return APIResponse(
                    False, 409, f"Invalid collaborator ID(s): {', '.join(invalid_ids)}"
                )

        # upload all the files to the cloudinary
        files_cloudinary_urls = []
        if len(validate_data.files) > 0:
            for file in validate_data.files:
                file_secure_url = cloudinary.uploader.upload(file)["secure_url"]

                files_cloudinary_urls.append(file_secure_url)

        # create the note document
        note = Notes.objects.create(
            user=found_user,
            title=validate_data.title,
            note=validate_data.note,
            files=files_cloudinary_urls,
        )

        # if the collaborators are given updaate the note 
        if validate_data.collaborators != None:
            collaborator_users = User.objects.filter(id__in=validate_data.collaborators)
            note.collaborators.set(collaborator_users)
            note.save()

        return APIResponse(True, 200, "Note has been created successfully.")
    except Exception:
        return APIResponse(False, 500, "Internal Server Error.")
