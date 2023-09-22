# api_view.py

from rest_framework import generics, permissions, status , viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import ShortURL , UserLocation
from .serializers import ShortURLCreateSerializer, ShortURLSerializer, ShortURLUpdateSerializer , UserLocationSerializer
from django.contrib.auth import login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
import string
from random import choices
from django.shortcuts import get_object_or_404


# code of custom authentication token geneator
class CustomAuthToken(ObtainAuthToken):
    """
    Custom Authentication Token
    ---------------------------

    This view allows a user to obtain an authentication token by providing valid credentials.

    **Authentication:**
    - Use the HTTP POST method to send user credentials (username and password) in the request body.
    - If valid, a token will be generated and returned.

    **Request Example:**
    ```
    POST /api-token-auth/
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

    **Response Example:**
    ```
    {
        "token": "your_auth_token"
    }
    ```

    **Status Codes:**
    - 200 OK: Authentication successful, token generated.
    - 400 Bad Request: Invalid credentials provided.

    **Notes:**
    - This endpoint should be used to obtain an authentication token for subsequent authenticated requests.

    **Example Usage:**
    To obtain an authentication token, make a POST request with valid credentials to `/api-token-auth/`.

    **Response Example (Success):**
    ```
    HTTP 200 OK
    {
        "token": "your_auth_token"
    }
    ```

    **Response Example (Failure):**
    ```
    HTTP 400 Bad Request
    {
        "non_field_errors": [
            "Unable to log in with provided credentials."
        ]
    }
    ```
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  code for creating a short url
class ShortURLCreateAPIView(generics.CreateAPIView):
    """
    Create Short URL
    ----------------

    This view allows an authenticated user to create a short URL.

    **Authentication:**
    - User must be authenticated.

    **Request Example:**
    ```
    POST /api/create-short-url/
    {
        "original_url": "https://example.com",
        "short_code": "custom_short_code"  # Optional
    }
    ```

    **Response Example (Success):**
    ```
    HTTP 201 Created
    {
        "message": "Short URL created successfully.",
        "short_url": "custom_short_code"
    }
    ```

    **Response Example (Failure - Short Code Already in Use):**
    ```
    HTTP 400 Bad Request
    {
        "message": "Short code is already in use. Please choose another one."
    }
    ```

    **Response Example (Failure - Validation Error):**
    ```
    HTTP 400 Bad Request
    {
        "field_name": [
            "Field specific validation error message."
        ]
    }
    ```

    **Notes:**
    - To create a short URL, make a POST request to `/api/create-short-url/`.
    - You can provide an optional custom short code; if not provided, a random one will be generated.
    - If the provided short code is already in use, a 400 Bad Request response is returned.
    - The generated or provided short URL is associated with the authenticated user.

    **Method Details:**
    The `generate_random_short_code` method generates a random 20-character short code if one is not provided.

    """

    serializer_class = ShortURLCreateSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Check if the user provided a custom short_code
        custom_short_code = serializer.validated_data.get('short_code') or self.generate_random_short_code()
        # Check if the provided short_code is already in use
        if custom_short_code and ShortURL.objects.filter(short_code=custom_short_code).exists():
            return Response(
                {"message": "Short code is already in use. Please choose another one."},
                status=HTTP_400_BAD_REQUEST,
            )
        
        # Save the ShortURL with the generated or provided short_code
        short_url = serializer.save(user=request.user, short_code=custom_short_code)
    
        # Return a response with the created ShortURL data
        return Response(
            {
                "message": "Short URL created successfully.",
                "short_url": short_url.short_code,
            },
            status=HTTP_201_CREATED,
        )

    def generate_random_short_code(self):
        # Generate a random 8-character short_code
        chars = string.ascii_letters + string.digits
        return ''.join(choices(chars, k=8))

class ShortURLListAPIView(generics.ListAPIView):
    """
    List Short URLs
    ---------------

    This view allows an authenticated user to retrieve a list of their short URLs.

    **Authentication:**
    - User must be authenticated.

    **Query Parameters:**
    - `limit` (optional): The maximum number of short URLs to retrieve (default is 10). 
    - Setting `limit` to "all" retrieves all short URLs.

    **Request Example (With Limit):**
    ```
    GET /api/short-urls/?limit=5
    ```

    **Request Example (Retrieve All Short URLs):**
    ```
    GET /api/short-urls/?limit=all
    ```

    **Response Example (Success):**
    ```
    HTTP 200 OK
    [
        {
            "id": 1,
            "original_url": "https://example.com",
            "short_code": "abc123",
            "expiry_date": "2023-12-31T23:59:59Z",
            "custom_note": "Example Note",
            "accurate_location_tracking": true
        },
        {
            "id": 2,
            "original_url": "https://example2.com",
            "short_code": "def456",
            "expiry_date": "2023-12-31T23:59:59Z",
            "custom_note": "Another Note",
            "accurate_location_tracking": false
        }
        // ... (other short URLs)
    ]
    ```

    **Notes:**
    - To retrieve a list of short URLs, make a GET request to `/api/short-urls/`.
    - You can specify the `limit` query parameter to limit the number of results or use "all" to retrieve all short URLs.

    """
    
    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter the queryset to only include short URLs of the authenticated user
        queryset = ShortURL.objects.filter(user=self.request.user)

        # Get the 'limit' query parameter from the request, or use a default value
        limit_param = self.request.query_params.get('limit', 10)  # Default limit is 10

        # Check if 'limit' is set to 'all', if so, return all results
        if isinstance(limit_param, str) and limit_param.lower() == 'all':
            return queryset

        # Validate and limit the number of results
        try:
            limit = int(limit_param)
            if limit <= 0:
                limit = 10  # Set a default limit if the value is invalid
        except ValueError:
            limit = 10  # Set a default limit if the value is not an integer

        return queryset[:limit]

class ShortURLUpdateAPIView(generics.UpdateAPIView):
    """
    Update Short URL
    ----------------

    This view allows an authenticated user to update the details of their short URL.

    **Authentication:**
    - User must be authenticated.

    **Request Example (Partial Update):**
    ```
    PATCH /api/short-urls/<short_url_id>/
    {
        "expiry_date": "2023-12-31T23:59:59Z",
        "password": "new_password"
    }
    ```

    **Request Example (Full Update):**
    ```
    PUT /api/short-urls/<short_url_id>/
    {
        "original_url": "https://newexample.com",
        "expiry_date": "2023-12-31T23:59:59Z",
        "password": "new_password",
        "custom_note": "Updated Note",
        "accurate_location_tracking": true
    }
    ```

    **Response Example (Success):**
    ```
    HTTP 200 OK
    {
        "message": "Short URL updated successfully."
    }
    ```

    **Notes:**
    - To update the details of a short URL, make a PATCH or PUT request to `/api/short-urls/<short_url_id>/`.
    - You can update specific fields, such as `expiry_date` or `password`, or provide a full update.
    - Ownership of the short URL is automatically verified based on the authenticated user.

    """
   
    serializer_class = ShortURLUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve ShortURLs related to the authenticated user
        return ShortURL.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Since we've filtered the queryset, there's no need to check ownership here
        serializer.save()

class ShortURLDeleteAPIView(generics.DestroyAPIView):
    """
    Delete Short URL
    ----------------

    This view allows an authenticated user to delete a short URL that they own.

    **Authentication:**
    - User must be authenticated.

    **Request Example:**
    ```
    DELETE /api/short-urls/<short_url_id>/
    ```

    **Response Example (Success):**
    ```
    HTTP 204 No Content
    ```

    **Response Example (Failure - Permission Denied):**
    ```
    HTTP 403 Forbidden
    {
        "detail": "You do not have permission to delete this ShortURL."
    }
    ```

    **Notes:**
    - To delete a short URL, make a DELETE request to `/api/short-urls/<short_url_id>/`.
    - Only the user who created the short URL can delete it. Others will receive a 403 Forbidden response if they try to delete it.

    """
    
    queryset = ShortURL.objects.all()
    serializer_class = ShortURLSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        # Ensure that only the user who created the ShortURL can delete it
        if instance.user == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this ShortURL.")


class ShortURLRetrieveAPIView(generics.RetrieveAPIView):
    """
    Retrieve Short URL by Short Code
    --------------------------------

    This view allows an authenticated user to retrieve the details of a short URL by its short code.

    **Authentication:**
    - User must be authenticated.

    **URL Parameters:**
    - `short_code` (str): The short code of the URL to retrieve.

    **Response Example (Success):**
    ```
    HTTP 200 OK
    {
        "id": 1,
        "original_url": "https://example.com",
        "short_code": "abc123",
        "expiry_date": "2023-12-31T23:59:59Z",
        "custom_note": "Example Note",
        "accurate_location_tracking": true
    }
    ```

    **Response Example (Failure - Not Found or No Access):**
    ```
    HTTP 404 Not Found
    {
        "detail": "You do not have access to this resource or it does not exist."
    }
    ```

    **Notes:**
    - To retrieve a short URL, make a GET request to `/api/short-urls/<short_code>/`.
    - If the short URL exists and the authenticated user is the author, its details are returned.
    - If the short URL does not exist or the user is not the author, a 404 Not Found response is returned.

    """
    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Get the 'short_code' from the URL parameters
        short_code = self.kwargs.get('short_code')
        
        # Use get_object_or_404 to retrieve the ShortURL instance by 'short_code'
        short_url = get_object_or_404(ShortURL, short_code=short_code)
        
        # Check if the authenticated user is the author of the ShortURL
        if short_url.user == request.user:
            # Serialize and return the ShortURL data
            serializer = self.get_serializer(short_url)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If the user is not the author, return a 404 error with a message
            return Response(
                {"detail": "You do not have access to this resource or it does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )


class UserLocationListAPIView(generics.ListAPIView):
    """
    List User Locations for a Short URL
    ------------------------------------

    This view allows an authenticated user to retrieve a list of user locations for a specific short URL.

    **Authentication:**
    - User must be authenticated.

    **URL Parameters:**
    - `short_code` (str): The short code of the URL for which user locations are to be retrieved.

    **Query Parameters:**
    - `limit` (optional): The maximum number of user locations to retrieve (default is 10).
    - Setting `limit` to "all" retrieves all user locations.

    **Request Example (With Limit):**
    ```
    GET /api/short-urls/locations/<short_code>/?limit=5
    ```

    **Request Example (Retrieve All User Locations):**
    ```
    GET /api/short-urls/locations/<short_code>/?limit=all
    ```

    **Response Example (Success):**
    ```
    HTTP 200 OK
    [
        {
            "id": 1,
            "latitude": 123.456,
            "longitude": 789.012,
            "timestamp": "2023-09-22T12:34:56Z"
        },
        {
            "id": 2,
            "latitude": 456.789,
            "longitude": 123.012,
            "timestamp": "2023-09-22T13:45:00Z"
        }
        // ... (other user locations)
    ]
    ```

    **Notes:**
    - To retrieve user locations for a short URL, make a GET request to `/api/short-urls/locations/<short_code>/`.
    - You can specify the `limit` query parameter to limit the number of results or use "all" to retrieve all user locations.

    """
    
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]
    default_limit = 10  # Default limit for the number of results
    all_limit_keyword = 'all'  # Keyword to request all results

    def get_queryset(self):
        # Get the 'short_code' from the URL parameters
        short_code = self.kwargs.get('short_code')

        # Use get_object_or_404 to retrieve the ShortURL instance by 'short_code'
        short_url = get_object_or_404(ShortURL, short_code=short_code)

        if short_url.user != self.request.user:
            # If the user is not the author, return an empty queryset (no access)
            return UserLocation.objects.none()
        # Get the 'limit' query parameter from the request
        limit = self.request.query_params.get('limit', self.default_limit)

        if limit == self.all_limit_keyword:
            # If 'limit' is set to 'all', return all user locations
            return UserLocation.objects.filter(short_url=short_url)

        try:
            limit = int(limit)
            if limit <= 0:
                limit = self.default_limit  # Set a default limit if the value is invalid
        except ValueError:
            limit = self.default_limit  # Set a default limit if the value is not an integer

        # If the user is the author, return the associated user locations with the limit
        return UserLocation.objects.filter(short_url=short_url)[:limit]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLocationRetrieveAPIView(generics.RetrieveAPIView):
    """
    Retrieve User Location for a Short URL
    ---------------------------------------

    This view allows an authenticated user to retrieve the details of a specific user location associated with a short URL.

    **Authentication:**
    - User must be authenticated.

    **URL Parameters:**
    - `short_code` (str): The short code of the URL for which the user location is to be retrieved.
    - `pk` (int): The primary key of the user location to retrieve.

    **Response Example (Success):**
    ```
    HTTP 200 OK
    {
        "id": 1,
        "latitude": 123.456,
        "longitude": 789.012,
        "timestamp": "2023-09-22T12:34:56Z"
    }
    ```

    **Response Example (Failure - Not Found or No Access):**
    ```
    HTTP 404 Not Found
    {
        "detail": "User location not found."
    }
    ```

    **Notes:**
    - To retrieve a specific user location associated with a short URL, make a GET request to `/api/short-urls/locations/<short_code>/<pk>/`.
    - If the user location exists and the authenticated user is the author of the short URL, its details are returned.
    - If the user location does not exist or the user is not the author, a 404 Not Found response is returned.

    """
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the 'short_code' from the URL parameters
        short_code = self.kwargs.get('short_code')

        # Use get_object_or_404 to retrieve the ShortURL instance by 'short_code'
        short_url = get_object_or_404(ShortURL, short_code=short_code)

        # Check if the authenticated user is the author of the ShortURL
        if short_url.user == self.request.user:
            # Return user locations associated with the ShortURL
            return UserLocation.objects.filter(short_url=short_url)
        else:
            # If the user is not the author, return an empty queryset (no access)
            return UserLocation.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # Get the 'pk' from the URL parameters
        pk = self.kwargs.get('pk')

        if user_location := self.get_queryset().filter(pk=pk).first():
            # Serialize and return the user location data
            serializer = self.get_serializer(user_location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If the user location is not found, return a 404 error
            return Response(
                {"detail": "User location not found."},
                status=status.HTTP_404_NOT_FOUND
            )







