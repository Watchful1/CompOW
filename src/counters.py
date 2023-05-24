import prometheus_client

queries = prometheus_client.Counter('bot_queries', "How many times we hit a site", ['site'])
process = prometheus_client.Counter('bot_process', "Each time we run through a type of check", ['type'])
events = prometheus_client.Gauge('bot_events', "How many events we're monitoring")


def init(port):
	prometheus_client.start_http_server(port)
