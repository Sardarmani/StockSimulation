
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Fetch user and generate token
user = User.objects.get(username="mani")  # Change "admin" to the actual username if needed
token, created = Token.objects.get_or_create(user=user)

print("Generated Token:", token.key)
# Token is Produced through Shell 6e55a79e9864540b89e668de631b79bf4d3ff191