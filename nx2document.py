import cassio
from cassio.config import check_resolve_session, check_resolve_keyspace
import networkx as nx

from langchain_openai import OpenAIEmbeddings
from langchain_community.graph_vectorstores.links import Link
from langchain_community.graph_vectorstores.cassandra import (
    CassandraGraphVectorStore,
    SetupMode,
    Document,
)


class NxToDocuments:
    def __init__(self, connect_to_database=True, reset_store=False):
        self.connect_to_database = connect_to_database
        self.reset_store = reset_store

        if self.connect_to_database:
            # Initialize cassandra connection from environment variables.
            cassio.init(auto=True)
            self.session = check_resolve_session()
            self.keyspace = check_resolve_keyspace()
            self.content_centric_store = CassandraGraphVectorStore(
                embedding=OpenAIEmbeddings(),
                node_table="graph_nodes",
                session=self.session,
                keyspace=self.keyspace,
                setup_mode=SetupMode.SYNC,
            )
        else:
            self.session = None
            self.keyspace = None
            self.content_centric_store = None

        if reset_store:
            self.session.execute(f"TRUNCATE TABLE {self.keyspace}.nodes")

    def nx_to_documents(self, graph: nx.DiGraph):
        for node in graph.nodes:
            try:
                node_data = graph.nodes[node]
                node_type = node_data.get("type", None)
                links = []
                for n in graph.neighbors(node):
                    links.append(Link.outgoing(kind=node_type, tag=n))

                document = Document(
                    id=node,
                    page_content=node_data.get("txt", "n/a"),
                    metadata={"type": node_type, "links": links},
                )

                self.content_centric_store.add_documents([document])
            except Exception as e:
                print(f"Failed to process node {node}: {e}")
            finally:
                yield document
