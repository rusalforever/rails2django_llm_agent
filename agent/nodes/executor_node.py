import logging
from agent.state import ConversionState


class ExecutorNode:
    """
    Центральний вузол, який координує виконання пайплайна.
    Він не імпортує graph безпосередньо, щоб уникнути циклічного імпорту.
    """

    def __init__(self, client, build_graph_func):
        """
        :param client: OpenAI клієнт
        :param build_graph_func: функція для побудови графа (передається ззовні)
        """
        self.client = client
        self.build_graph_func = build_graph_func

    def run(self, state: ConversionState):
        logging.info("🧩 ExecutorNode started — building conversion pipeline...")
        graph = self.build_graph_func(self.client)
        app = graph.compile()

        logging.info("🚀 Executing full conversion pipeline...")
        final_state = app.invoke(state)

        logging.info("✅ ExecutorNode finished all steps successfully.")
        return final_state
