from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


# def full_details_exception_handler(exc, content):
#     if isinstance(exc, APIException):
#         exc.detail = exc.get_full_details()
#     return exception_handler(exc, content)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {'errors': []}

        for key, value in response.data.items():
            error = {'field': key, 'message': value}
            custom_response['errors'].append(error)

        response.data = custom_response
    return response
