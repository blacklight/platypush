from typing import Optional, Union, List, Dict, Any

import requests

from platypush.plugins import Plugin, action


class Covid19Plugin(Plugin):
    """
    Monitor the diffusion data of the COVID-19 pandemic by using the public API at https://api.covid19api.com.
    """

    base_url = 'https://api.covid19api.com'

    def __init__(self, country: Union[str, List[str]] = 'world', **kwargs):
        """
        :param country: Default country (or list of countries) to retrieve the stats for. It can either be the full
            country name or the country code. Special values:

            - ``world``: Get worldwide stats (default).
            - ``all``: Get all the available stats.
        """
        super().__init__(**kwargs)
        self.country = []
        self.all_countries = requests.get('{}/countries'.format(self.base_url)).json()
        self.country = self._get_countries(country)

    def _get_countries(self, country: Optional[Union[str, List[str]]] = None) -> List[str]:
        country = country or self.country
        if isinstance(country, str):
            country = country.split(',')
        lc_country = {c.lower() for c in country}
        return [c['ISO2'] for c in self.all_countries
                if c['ISO2'].lower() in lc_country
                or c['Slug'].lower() in lc_country
                or c['Country'].lower() in lc_country]

    @action
    def summary(self, country: Optional[Union[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        Get the summary data for the world or a country.

        :param country: Default country override.
        """
        countries = self._get_countries(country)
        response = requests.get('{}/summary'.format(self.base_url)).json()
        if countries[0] == 'all':
            return response.get('Countries', [])
        if countries[0] == 'world':
            return response.get('Global', {})

        return [
            c for c in response.get('Countries', [])
            if c.get('CountryCode').upper() in countries
            or c.get('Country').upper() in countries
        ]

    @action
    def data(self, country: Optional[Union[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        Get all the data for a country.

        :param country: Default country override.
        """
        countries = self._get_countries(country)
        ret = []
        for country in countries:
            ret += requests.get('{}/total/country/{}'.format(self.base_url, country)).json()
        return ret


# vim:sw=4:ts=4:et:
