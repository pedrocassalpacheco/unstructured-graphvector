import networkx as nx
from unstructured.cleaners.core import clean
from pyvis.network import Network
import logging

# Create a logger for this file
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Doc2Graph:
    def __init__(self, file_name, infer_hierarchy=True):
        self.name = "Default Element"

        # NetworkX graph to store the document structure
        self.graph = nx.DiGraph()
        self.graph.add_node(file_name, type="document")
        self.root_node = file_name
        self.infer_hierarchy = infer_hierarchy

        self.element_handlers = {
            "Formula": self.handle_formula,
            "FigureCaption": self.handle_figure_caption,
            "NarrativeText": self.handle_narrative_text,
            "ListItem": self.handle_list_item,
            "Title": self.handle_title,
            "Address": self.handle_address,
            "EmailAddress": self.handle_email_address,
            "Image": self.handle_image,
            "PageBreak": self.handle_page_break,
            "Table": self.handle_table,
            "Header": self.handle_header,
            "Footer": self.handle_footer,
            "CodeSnippet": self.handle_code_snippet,
            "PageNumber": self.handle_page_number,
            "UncategorizedText": self.handle_uncategorized_text,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def display(self):
        return ""

    def handle_formula(self, element):
        return ""

    def handle_figure_caption(self, element):
        self.graph.add_node(
            element.id,
            type="figure_caption",
            txt=element.text,
            **element.metadata.to_dict(),
        )
        self.handle_hierarchy(element)
        return

    def handle_narrative_text(self, element):
        self.graph.add_node(
            element.id,
            type="narravite_text",
            txt=element.text,
            **element.metadata.to_dict(),
        )
        self.handle_hierarchy(element)
        return

    def handle_list_item(self, element):
        self.graph.add_node(
            element.id, type="list_item", txt=element.text, **element.metadata.to_dict()
        )
        self.handle_hierarchy(element)
        return

    def handle_title(self, element):
        self.graph.add_node(
            element.id, type="section", txt=element.text, **element.metadata.to_dict()
        )
        self.handle_hierarchy(element)
        self.last_title = element.id
        return

    def handle_address(self, element):
        return

    def handle_email_address(self, element):
        return

    def handle_image(self, element):
        self.graph.add_node(
            element.id, type="image", txt=element.text, **element.metadata.to_dict()
        )
        self.handle_hierarchy(element)
        return

    def handle_page_break(self, element):
        return

    def handle_table(self, element):
        self.graph.add_node(
            element.id, type="table", txt=element.text, **element.metadata.to_dict()
        )
        self.handle_hierarchy(element)
        return

    def handle_header(self, element):
        return

    def handle_footer(self, element):
        return

    def handle_code_snippet(self, element):
        return

    def handle_page_number(self, element):
        return

    def handle_uncategorized_text(self, element):
        return

    # Handles element hierarchy
    def handle_hierarchy(self, element):
        if type(element).__name__ == "Title":
            self.graph.add_edge(self.root_node, element.id, edge_type="root")
        elif self.infer_hierarchy is False and element.metadata.parent_id is not None:
            self.graph.add_edge(
                element.metadata.parent_id, element.id, edge_type="inheritance"
            )
        else:
            self.graph.add_edge(self.last_title, element.id, edge_type="inferred")
        return

    # Mapping element types to their handling functions
    def process_element(self, element):
        # Extract the element type from the class name
        element_type = type(element).__name__

        handler = self.element_handlers.get(element_type)
        if handler:
            return handler(element)
        else:
            return "Unknown element type."

    def get_graph(self):
        return self.graph

    def plot_graph(self, file_name):
        net = Network(
            notebook=True,
            cdn_resources="in_line",
            bgcolor="#222222",
            font_color="white",
            height="750px",
            width="100%",
        )
        # Convert the NetworkX graph to a PyVis graph
        for n in self.graph.nodes(data=True):
            try:
                n[1]["label"] = n[0] + " " + n[1]["type"]
            except Exception as e:
                logger.error(
                    f"Unable to set label for node {n[0]} while plotting graph: {e}"
                )

        net.from_nx(self.graph)

        # Render the graph in the Jupyter notebook
        net.show_buttons()
        net.show(file_name + ".html")

    def clean(self, text):
        return clean(text, bullets=True, extra_whitespace=True, lowercase=True)
