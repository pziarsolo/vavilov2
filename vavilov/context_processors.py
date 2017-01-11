from vavilov.conf import settings


def googlemapkey(request):
    try:
        googlemapkey = settings.GOOGLEMAPKEY
    except:
        googlemapkey = None

    return {'googlemapkey': googlemapkey}
