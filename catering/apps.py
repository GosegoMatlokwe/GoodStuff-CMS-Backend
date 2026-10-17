# Import the base AppConfig class from Django
from django.apps import AppConfig

# This class configures the 'catering' app when Django starts up
class CateringConfig(AppConfig):
    # 'name' tells Django the exact Python path to your app
    name = 'catering'