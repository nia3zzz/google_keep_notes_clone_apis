from rest_framework.decorators import api_view
from ..utils.api_response import APIResponse
from pydantic import ValidationError
from ..validators.note_validators import CreateNoteValidator, UpdateNoteValidator
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


# creating a view to let the user or contributer update the note
@api_view(["PUT"])
def update_note(request, note_id):
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

    data = {
        "note_id": note_id,
        "title": request.data.get("title"),
        "note": request.data.get("note"),
        "files_urls": request.data.getlist("files_urls"),
        "files": request.FILES.getlist("files"),
    }

    try:
        # after successful authentication it's time to validate the data recieved from this request that includes teh request body and the parameter of note id
        validate_data = UpdateNoteValidator(**data)
    except ValidationError as e:
        return APIResponse(False, 400, "Failed in type validation.", error=e.errors())

    try:
        # check if the note exists with the note id provided as parameter in request url
        found_note = Notes.objects.get(id=validate_data.note_id)
    except Notes.DoesNotExist:
        return APIResponse(False, 404, "Note not found with this id.")

    # check if the user trying to update the note is allowed of their action
    if (
        found_user.id != found_note.user.id
        and found_user.id not in found_note.collaborators
    ):
        return APIResponse(False, 401, "You are not authorized to update this note.")

    # check if the fields are updated and not the same as it was
    if (
        validate_data.title == found_note.title
        and validate_data.note == found_note.note
        and validate_data.files_urls == found_note.files
        and validate_data.files == None
    ):
        return APIResponse(False, 409, "No changes found to update.")

    try:

        # upload the file and hold the secure url if an file has been provided
        files_cloudinary_urls = []
        if len(validate_data.files) > 0:
            for file in validate_data.files:
                file_secure_url = cloudinary.uploader.upload(file)["secure_url"]

                files_cloudinary_urls.append(file_secure_url)

        if len(files_cloudinary_urls) > 0:
            # update the note now
            found_note.title = validate_data.title
            found_note.note = validate_data.note
            files = validate_data.files_urls or []
            files.extend(files_cloudinary_urls)
            found_note.files = files
            found_note.save()

            return APIResponse(True, 200, "Note has been updated.")

        # if no new files are given
        found_note.title = validate_data.title
        found_note.note = validate_data.note
        found_note.files = validate_data.files_urls
        found_note.save()

        return APIResponse(True, 200, "Note has been updated.")

    except Exception:
        return APIResponse(False, 500, "Internal server error.")
