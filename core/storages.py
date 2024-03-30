from storages.backends.azure_storage import AzureStorage
from django.conf import settings

class AzureMediaStorage(AzureStorage):
    account_name = settings.STORAGE_ACCOUNT_NAME 
    account_key = settings.STORAGE_ACCOUNT_KEY
    expiration_secs = None
    azure_container = 'media'


class AzureStaticStorage(AzureStorage):
    account_name = settings.STORAGE_ACCOUNT_NAME 
    account_key = settings.STORAGE_ACCOUNT_KEY
    azure_container = 'static'
    expiration_secs = None