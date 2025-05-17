import jwt
import os
from .models import Session

ENV_SECRET_KEY = os.getenv("JWT_SECRET")


# there will be 2 function for authentication a initialize token and verification of token
def initializeToken(user):  # take the user dictionary as the parameter
    try:
        # encode and sign the token with id, secret and the preffered algorithm
        encoded_jwt = jwt.encode(
            {"id": str(user.id)}, ENV_SECRET_KEY, algorithm="HS256"
        )

        # save the session in the database
        Session.objects.create(user=user)

        return encoded_jwt  # return the token from the function
    except Exception:
        raise RuntimeError("An error occured in initializeToken function.")


def verifyToken(request):  # get the request object as the parameter from the view
    # the cookie token from the request
    cookie_token = request.COOKIES.get("token")

    # if there is no token
    if cookie_token == None:
        return False

    # decode the token with cookie, secret and algorithms
    decode_token = jwt.decode(cookie_token, ENV_SECRET_KEY, algorithms=["HS256"])

    # if the decode method has failed to verify
    if decode_token == False:
        return False

    # check if the sessions exists
    found_session = Session.objects.filter(user=decode_token.get("id"))

    if not found_session.exists():
        return False

    # return the decoded id to the view it was called from
    return decode_token.get("id")
