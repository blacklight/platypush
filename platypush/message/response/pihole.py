from platypush.message.response import Response


class PiholeStatusResponse(Response):
    def __init__(self,
                 server: str,
                 status: str,
                 ads_percentage: float,
                 blocked: int,
                 cached: int,
                 domain_count: int,
                 forwarded: int,
                 queries: int,
                 total_clients: int,
                 total_queries: int,
                 unique_clients: int,
                 unique_domains: int,
                 version: str,
                 *args,
                 **kwargs):
        super().__init__(*args, output={
            'server': server,
            'status': status,
            'ads_percentage': ads_percentage,
            'blocked': blocked,
            'cached': cached,
            'domain_count': domain_count,
            'forwarded': forwarded,
            'queries': queries,
            'total_clients': total_clients,
            'total_queries': total_queries,
            'unique_clients': unique_clients,
            'unique_domains': unique_domains,
            'version': version,
        }, **kwargs)


# vim:sw=4:ts=4:et:
