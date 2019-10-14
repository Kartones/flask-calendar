DEBUG = True
DATA_FOLTER = "data"
USERS_DATA_FOLDER = "users"
BASE_URL = "http://127.0.0.1:5000"
MIN_YEAR = 2017
MAX_YEAR = 2100
PASSWORD_SALT = "something random and full of non-standard characters"
HOST_IP = "0.0.0.0"  # set to None for production
LOCALE = "es_ES.UTF-8"
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "Europe/Madrid"
MONTHS_TO_EXPORT = 6  # currently only used for ICS export

FEATURE_FLAG_ICAL_EXPORT = False

# (base ^ attempts ) second delays between failed logins
FAILED_LOGIN_DELAY_BASE = 2

# If true, will automatically decorate hyperlinks with <a> tags upon rendering them
AUTO_DECORATE_TASK_DETAILS_HYPERLINK = True

SHOW_VIEW_PAST_BUTTON = True

# Of use if SHOW_VIEW_PAST_BUTTON is active
HIDE_PAST_TASKS = False
