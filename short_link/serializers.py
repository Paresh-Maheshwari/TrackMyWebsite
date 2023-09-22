# serializers.py
from rest_framework import serializers
from .models import *



"""
Serializes ShortURL instances into Python data types and vice versa.

The ShortURLSerializer class is a subclass of the ModelSerializer class provided by the Django REST Framework. It defines the serialization behavior for the ShortURL model.

Args:
    serializers.ModelSerializer: The base class for the ShortURLSerializer class.

Returns:
    None

"""
class ShortURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        exclude = ('user',) 

    def get_fields(self):
        fields = super().get_fields()
        if 'fields' in self.context['request'].query_params:
            # Split the 'fields' query parameter and include only the specified fields
            included_fields = self.context['request'].query_params['fields'].split(',')
            for field_name in list(fields.keys()):
                if field_name not in included_fields:
                    fields.pop(field_name)
        return fields


"""
The Meta class defines the metadata options for the ShortURLSerializer class.

The Meta class specifies the model to be used for serialization (ShortURL) and the fields to include in the serialized representation.

Args:
    None

Returns:
    None
"""
class ShortURLUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortURL
        fields = ['original_url', 'expiry_date', 'password', 'custom_note', 'accurate_location_tracking']



"""
Serializes ShortURL instances into Python data types and vice versa.

The ShortURLSerializer class is a subclass of the ModelSerializer class provided by the Django REST Framework. It defines the serialization behavior for the ShortURL model.

Args:
    serializers.ModelSerializer: The base class for the ShortURLSerializer class.

Returns:
    None
"""

class ShortURLCreateSerializer(serializers.ModelSerializer):
    short_code = serializers.CharField(max_length=20, required=False)
    class Meta:
        model = ShortURL
        fields = [
            'original_url',
            'expiry_date',
            'password',
            'custom_note',
            'accurate_location_tracking',
            'short_code',  # Include the custom_short_code field if needed
        ]




"""
Serializes UserLocation instances into Python data types and vice versa.

The UserLocationSerializer class is a subclass of the ModelSerializer class provided by the Django REST Framework. It defines the serialization behavior for the UserLocation model.

Args:
    serializers.ModelSerializer: The base class for the UserLocationSerializer class.

Returns:
    None
"""

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        exclude = ('short_url', 'author')
        





