from rest_framework.response import Response
from django.utils import timezone


# a standardized api response function that uses the django rest framework's response class to send back the api response to the client while maintaing a clean code base
def APIResponse(
    success: bool, status_code: int, message: str, data=None, cookie=None, error=None
):

    # creation of the response dictionary
    response_body = {
        "success": success,
        "statusCode": status_code,
        "message": message,
        "data": data if success else None,
        "error": error if not success else None,
        "meta": {
            "timestamp": timezone.now().isoformat(),
        },
    }

    # initialize the response object with the response body
    response = Response(response_body, status=status_code)

    # if there is a cookie in the login function
    if cookie:
        response.set_cookie(
            key="token", value=cookie, httponly=True, secure=False, samesite="Lax"
        )
    
    return response
