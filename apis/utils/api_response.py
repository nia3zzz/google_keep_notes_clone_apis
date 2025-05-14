from rest_framework.response import Response
from django.utils import timezone


# a standardized api response function that uses the django rest framework's response class to send back the api response to the client while maintaing a clean code base
def APIResponse(success: bool, status_code: int, message: str, data=None, error=None):

    # creation of the response dictionary
    response = {
        "success": success,
        "statusCode": status_code,
        "message": message,
        "data": data if success else None,
        "error": error if not success else None,
        "meta": {
            "timestamp": timezone.now().isoformat(),
        },
    }

    return Response(response, status=status_code)
