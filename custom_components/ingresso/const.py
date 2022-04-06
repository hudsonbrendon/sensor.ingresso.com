from datetime import timedelta

BASE_URL = "https://api-content.ingresso.com/v0/templates/nowplaying/{}?partnership={}"
ICON = "mdi:ticket"

CONF_CITY_ID = "city_id"
CONF_CITY_NAME = "city_name"
CONF_PARTNERSHIP = "partnership"
SCAN_INTERVAL = timedelta(minutes=120)
