from rest_framework.decorators import api_view
from pydantic import ValidationError
from ..utils.api_response import APIResponse
from ..validators.user_validators import (
    CreateUserValidator,
    LoginValidator,
    GetUserValidator,
)
from users.models import User
import bcrypt
import cloudinary.uploader
from auth_sessions.utils import initializeToken, verifyToken
from auth_sessions.models import Session
from rest_framework.response import Response
from django.utils import timezone
from ..serializers.user_serializers import UsersSerializer

# when using the post request method make sure to create a user and during the get request method get a single user using the provided email in the request body for adding user in the list of collaborators
@api_view(["POST", "GET"])
def create_or_get_user(request):
    if request.method == "POST":
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
            return APIResponse(
                False, 400, "Failed in type validation.", error=e.errors()
            )

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
        
    elif request.method == "GET":
        try:
            # validate the request body's email field
            validated_data = GetUserValidator(**request.data)
        except ValidationError as e:
            return APIResponse(
                False, 400, "Failed in type validation.", error=e.errors()
            )

        try:
            # look up for any existing user using the type validated email
            found_user = User.objects.get(email=validated_data.email)
        except User.DoesNotExist:
            return APIResponse(False, 404, "User not found with this email.")

        try:
            # serialize the data of the found user and send back data to the client
            serialized_found_user = UsersSerializer(found_user)

            return APIResponse(
                True,
                200,
                "User found with this email.",
                data=serialized_found_user.data,
            )
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


@api_view(["POST"])
def logout(request):
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
        # delete the session in database
        Session.objects.filter(user=found_user).delete()

        # return response to the client
        response = Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "User has been logged out.",
                "data": None,
                "error": None,
                "meta": {
                    "timestamp": timezone.now().isoformat(),
                },
            },
            status=200,
        )

        # delete the cookie named token by calling a method on the reponse object
        response.delete_cookie("token")

        return response
    except Exception:
        return APIResponse(False, 500, "Internal Server Error.")
