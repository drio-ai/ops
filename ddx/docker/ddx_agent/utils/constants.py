import os


class Constants:
    ACCEPT_HDR                  = "Accept"
    AUTH_HDR                    = "Authorization"
    AUTH_HDR_VALUE              = "Bearer {token}"
    APPLICATION_JSON_HDR_VALUE  = "application/json; charset=utf-8"
    PROPERTIES_FILE_DIR         = "/var/log"
    PROPERTIES_FILE_NAME        = os.path.join(PROPERTIES_FILE_DIR, "common.properties")
    CLUSTER_TOKEN               = "cluster_token"
    DRIO_DEFAULT_BASE_ENDPOINT = 'controller.ddx.drio.ai/api/v1/'
    AWS_META_SERVER             = '169.254.169.254'
    KAFKA_ENDPOINTS             = 'kafka.endpoints'
    SR_ENDPOINTS                = 'kafka.schema.registry.endpoints'
    DDX_ID_STORE                = '/docker-entrypoint-ddx.d/UUID'
    AGENT_RESTART_COUNT_STORE   = '/docker-entrypoint-ddx.d/ddx_agent_restart_count'
    SE_RESTART_COUNT_STORE      = '/docker-entrypoint-ddx.d/se_restart_count'
    LOCAL_WS                    = 'ws://127.0.0.1:8080/greeting/websocket'
    KAFKA_CONFIG_SECTION        = 'data_source_kafka'
    KAFKA_JSON_DATASETS         = 'KAFKA_JSON_DATASETS'
    KAFKA_DATASET_CONFIG        = 'kafka.datasets'
    SUBJECT_METADATA            = 'resources/subject_metadata.json'
    CLUSTER_MODELS              = 'resources/cluster_models.pkl'
    MONITORED_SUBJECTS          = 'monitored_subjects'
    KAFKA_DS_IS                 = 'kafka.id'
    KAFKA_METRICS_FILE          = '/docker-entrypoint-ddx.d/ddx_agent/utils/kafka_metrics.json'
    KAFKA_BROKER_METRICS        = "brokerMetrics"
    KAFKA_CONSUMER_METRICS      = "consumerMetrics"
    KAFKA_PRODUCER_METRICS      = "producerMetrics"



    USERNAME                    = os.environ.get('USERNAME')
    PASSWORD                    = os.environ.get('PASSWORD')
    IP                          = os.environ.get('BROKER_IP')  # Kafka broker  instance ip
    TOPIC_NAME                  = "pwdtopic"     
    GROUP_ID                    = "pdf_processor_group"   # if 
    SERVER_PORT                 = 9999
    PRODUCER_PORT               = 9998
    CONSUMER_PORT               = 9997
    FETCH_INTERVAL              = 5  # in seconds # if
    METRICS_TYPE                = 'producer'

    #PDF extracter 



class Model:
    IP                          = os.environ.get('BROKER_IP')  # Kafka broker  instance ip
    GROUP_ID                    = "pdf_processor_group"
    TOPIC_NAME                  = "pwdtopic" 
    CONSUMER_PORT               = '9092'    
    










