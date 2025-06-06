from rest_framework.decorators import api_view
from ..utils.api_response import APIResponse
from pydantic import ValidationError
from ..validators.note_validators import (
    CreateNoteValidator,
    UpdateNoteValidator,
    DeleteNoteValidator,
    AddRemoveCollaboratorValidator,
)
from auth_sessions.utils import verifyToken
from users.models import User
import cloudinary.uploader
from notes.models import Notes
from django.db.models import Q
from ..serializers.note_serializers import NotesSerializer


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


# creating a view to let the user or contributer update the note and also have the user delete their note based on their provided note id and http methods provided
@api_view(["PUT", "DELETE"])
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

    if request.method == "PUT":
        data = {
            "note_id": note_id,
            "title": request.data.get("title"),
            "note": request.data.get("note"),
            "files_urls": request.data.getlist("files_urls"),
            "files": request.FILES.getlist("files"),
        }

        try:
            # after successful authentication it's time to validate the data recieved from this request that includes teh request body and the parameter of note id
            validate_put_method_data = UpdateNoteValidator(**data)
        except ValidationError as e:
            return APIResponse(
                False, 400, "Failed in type validation.", error=e.errors()
            )

        try:
            # check if the note exists with the note id provided as parameter in request url
            found_note = Notes.objects.get(id=validate_put_method_data.note_id)
        except Notes.DoesNotExist:
            return APIResponse(False, 404, "Note not found with this id.")

        # check if the user trying to update the note is allowed of their action
        if (
            found_user.id != found_note.user.id
            and found_user.id not in found_note.collaborators
        ):
            return APIResponse(
                False, 401, "You are not authorized to update this note."
            )

        # check if the fields are updated and not the same as it was
        if (
            validate_put_method_data.title == found_note.title
            and validate_put_method_data.note == found_note.note
            and validate_put_method_data.files_urls == found_note.files
            and validate_put_method_data.files == None
        ):
            return APIResponse(False, 409, "No changes found to update.")

        try:

            # upload the file and hold the secure url if an file has been provided
            files_cloudinary_urls = []
            if len(validate_put_method_data.files) > 0:
                for file in validate_put_method_data.files:
                    file_secure_url = cloudinary.uploader.upload(file)["secure_url"]

                    files_cloudinary_urls.append(file_secure_url)

            if len(files_cloudinary_urls) > 0:
                # update the note now
                found_note.title = validate_put_method_data.title
                found_note.note = validate_put_method_data.note
                files = validate_put_method_data.files_urls or []
                files.extend(files_cloudinary_urls)
                found_note.files = files
                found_note.save()

                return APIResponse(True, 200, "Note has been updated.")

            # if no new files are given
            found_note.title = validate_put_method_data.title
            found_note.note = validate_put_method_data.note
            found_note.files = validate_put_method_data.files_urls
            found_note.save()

            return APIResponse(True, 200, "Note has been updated.")

        except Exception:
            return APIResponse(False, 500, "Internal server error.")

    elif request.method == "DELETE":
        try:
            # validate the request parameter of note id
            validate_delete_method_data = DeleteNoteValidator(note_id=note_id)
        except ValidationError as e:
            return APIResponse(
                False, 400, "Failed in type validation.", error=e.error()
            )

        try:
            # check if a note exists with the provided note id request url parameter
            found_note = Notes.objects.get(id=validate_delete_method_data.note_id)
        except Notes.DoesNotExist:
            return APIResponse(False, 404, "Note not found with this id.")

        # check if the user making the request is the creator of the note
        if found_user.id != found_note.user.id:
            return APIResponse(False, 401, "Unauthorized")

        try:
            # delete the note and return a successful response
            found_note.delete()
            found_note.save()

            return APIResponse(True, 200, "Note has been deleted.")
        except Exception:
            return APIResponse(False, 500, "Internal server error.")


# this api controller function will send back notes of users and collaborator where the user has created or marked as a collaborator
@api_view(["GET"])
def get_notes(request):
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

    # get all the notes where the user is the creator
    try:
        # get all the notes where the user is the creator
        found_notes = Notes.objects.filter(
            Q(user_id=found_user.id) | Q(collaborators=found_user.id)
        ).distinct()

        # serialize the notes
        serialized_found_notes = NotesSerializer(found_notes, many=True)

        return APIResponse(
            True, 200, "Notes have been fetched.", data=serialized_found_notes.data
        )

    except Exception:
        return APIResponse(False, 500, "Internal server error.")


@api_view(["POST", "DELETE"])
def add_remove_collaborator(request, note_id):
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

    try:

        # validate the request url parameter and the body for the id of the potential collaborator
        validated_data = AddRemoveCollaboratorValidator(note_id=note_id, **request.data)
    except ValidationError as e:
        return APIResponse(False, 400, "Failed in type validation.", error=e.errors())

    try:

        # check if the provided note id's note exists in the database
        found_note = Notes.objects.get(id=validated_data.note_id)
    except Notes.DoesNotExist:
        return APIResponse(False, 404, "No note found with this id.")

    try:
        # check if the provided user's id
        found_collaborator = User.objects.get(id=validated_data.collaborator_id)
    except User.DoesNotExist:
        return APIResponse(False, 404, "No user found with this id.")

    # check if the user himself is trying to make changes of himself as a collaborator
    if found_user == found_collaborator:
        return APIResponse(False, 409, "Can not make changes of yourself.")

    # if the request made to this url is a post we will add a collaborator of this id
    if request.method == "POST":
        # check if the user is already a collaborator
        if found_note.collaborators.filter(id=found_collaborator.id).exists():
            return APIResponse(False, 409, "This user is already a collaborator.")

        # save the user as a collaborator
        found_note.collaborators.add(found_collaborator)
        return APIResponse(True, 200, "This user has been added as a collaborator.")
    elif request.method == "DELETE":
        # check if the user is not in the collaborators
        if found_note.collaborators.filter(id=found_collaborator.id).exists() == False:
            return APIResponse(False, 409, "This user is not a collaborator.")

        # save the user as a collaborator
        found_note.collaborators.remove(found_collaborator)
        return APIResponse(True, 200, "This user has been removed from a collaborator.")
