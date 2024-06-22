"""
Common Torrents CSV constants.
"""

TORRENT_CSV_API_URL = 'https://torrents-csv.com/service'
""" Default Torrents CSV API base URL. """

TORRENTS_CSV_DOWNLOAD_URL = 'https://git.torrents-csv.com/heretic/torrents-csv-data/raw/branch/main/torrents.csv'
""" Default torrents.csv download URL. """

TORRENTS_CSV_URL_LAST_CHECKED_VAR = '_TORRENTS_CSV_URL_LAST_CHECKED'
""" Environment variable to store the last checked timestamp for the torrents.csv URL. """

TORRENTS_CSV_DEFAULT_CHECK_INTERVAL = 60 * 60 * 24
""" Interval in seconds to re-check the torrents.csv URL (24 hours). """
