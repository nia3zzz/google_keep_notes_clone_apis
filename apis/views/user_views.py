from rest_framework.decorators import api_view
from pydantic import ValidationError
from ..utils.api_response import APIResponse
from ..validators.user_validators import CreateUserValidator, LoginValidator
from users.models import User
import bcrypt
import cloudinary.uploader
from auth_sessions.utils import initializeToken


@api_view(["POST"])
def create_user(request):
    data = {
        "name": request.data.get("name"),
        "email": request.data.get("email"),
        "profile_picture": request.FILES.get("profile_picture"),
        "password": request.data.get("password"),
    }

    # make the data go through a pydentic validator to check for the expected data type
    try:
        validate_data = CreateUserValidator(**data)
    except ValidationError as e:
        return APIResponse(False, 400, "Failed in type validation.", error=e.errors())

    # check for any duplicate items with the email
    if User.objects.filter(email=validate_data.email).exists():
        return APIResponse(False, 409, "User with this email already exists.")

    try:
        # hash the user's password
        generated_salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(
            validate_data.password.encode("utf-8"), generated_salt
        )

        # upload the image to cloudinary and hold the secure url
        profile_picture_secure_url = cloudinary.uploader.upload(
            validate_data.profile_picture
        )["secure_url"]

        # create a user
        User.objects.create(
            name=validate_data.name,
            email=validate_data.email,
            profile_picture_url=profile_picture_secure_url,
            password=hashed_password.decode(),
        )

        return APIResponse(True, 201, "User has been created.")
    except Exception:
        return APIResponse(False, 500, "Internal Server Error.")


@api_view(["POST"])
def login(request):
    try:
        # validate the request body
        validate_data = LoginValidator(**request.data)
    except ValidationError as e:
        return APIResponse(False, 400, "Failed in type validation.", error=e.errors())

    try:
        # get hold of the user
        found_user = User.objects.get(email=validate_data.email)
    except User.DoesNotExist:
        return APIResponse(False, 409, "Invalid Credentials.")

    # check if the password is correct
    if (
        bcrypt.checkpw(
            validate_data.password.encode("utf-8"), found_user.password.encode("utf-8")
        )
    ) == False:
        return APIResponse(False, 409, "Invalid Credentials.")

    # initialize the token and send reponse to the client
    try:
        token = initializeToken(found_user)
        return APIResponse(True, 200, "User has been logged in.", cookie=token)
    except Exception:
        return APIResponse(False, 500, "Internal Server Error.")
