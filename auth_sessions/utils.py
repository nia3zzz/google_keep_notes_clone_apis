import jwt
import os
from .models import Session
from rest_framework.response import Response


# there will be 2 function for authentication a initialize token and verification of token
def initializeToken(user):
    try:
        ENV_SECRET_KEY = os.getenv("JWT_SECRET")

        encoded_jwt = jwt.encode(
            {"id": str(user.id)}, ENV_SECRET_KEY, algorithm="HS256"
        )

        Session.objects.create(user=user)

        return encoded_jwt
    except Exception:
        raise RuntimeError("An error occured in initializeToken function.")
