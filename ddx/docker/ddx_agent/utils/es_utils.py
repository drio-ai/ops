import optparse

from elasticsearch import Elasticsearch

ES_URL = "http://localhost:9200"
ES_BASIC_AUTH = ('elastic', 'IDRkD4gXF-5cVsE=hVMQ')
ES_SCHEMA_INDEX_NAME = 'json_schema'


def add_dummy_schema():
    es_client = Elasticsearch(ES_URL, basic_auth=ES_BASIC_AUTH)
    es_client.index(
        index=ES_SCHEMA_INDEX_NAME,
        id="topic-schema-1",
        document={
            "foo": "text",
            "bar": "long",
        }
    )


if __name__ == '__main__':
    # create OptionParser object
    usage = "usage: es_utils.py [options] arg1 arg2"
    parser = optparse.OptionParser(usage=usage)

    # add options
    parser.add_option('--es-schema', dest='es_schema',
                      action='store_true',
                      default=False,
                      help='populate dummy schema in ES')

    (options, args) = parser.parse_args()

    if options.es_schema:
        add_dummy_schema()
    else:
        print(parser.usage)
        exit(0)

