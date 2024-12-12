import logging
import xmlrpc.client as xc

SYSTEM_PROCESSES = ['ddx:ddx-agent', 'ddx:stream-engine']
INET_HTTP = 'http://localhost:9001'

# logger
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


class SupervisorConnector:
    def __init__(self, agent_restart_count_store, stream_engine_restart_count_store):
        self.process_map_to_store = {
            'ddx:ddx-agent': agent_restart_count_store,
            'ddx:stream-engine': stream_engine_restart_count_store
        }
        self.rpc_client = xc.ServerProxy(INET_HTTP)

    def get_process_stats(self, processes):
        stats_collector = {}
        if processes is None:
            processes = []

        for p in processes:
            if p in SYSTEM_PROCESSES:
                try:
                    stats_collector[p] = self.rpc_client.supervisor.getProcessInfo(p)
                    restart_count = 0
                    with open(self.process_map_to_store.get(p, 'noop'), 'r') as f:
                        restart_count = int(f.read())

                    stats_collector[p]['restart_count'] = restart_count
                except Exception as e:
                    logging.error(e)

        return stats_collector

    def reload_process(self, ddx_process):
        try:
            self.rpc_client.supervisor.stopProcess(ddx_process)
            self.rpc_client.supervisor.startProcess(ddx_process)
        except Exception as e:
            logging.error(e)

