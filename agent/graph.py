from langgraph.graph import StateGraph
from agent.state import ConversionState
from openai import OpenAI
import logging
from agent.nodes.planner_node import LLMPlannerNode
from agent.nodes.discovery_node import LLMDiscoveryNode
from agent.nodes.converter_node import LLMConverterNode
from agent.nodes.builder_node import LLMProjectBuilderNode
from agent.nodes.integration_node import LLMIntegrationNode


def build_conversion_graph(client):
    from agent.nodes.planner_node import LLMPlannerNode
    from agent.nodes.discovery_node import LLMDiscoveryNode
    from agent.nodes.converter_node import LLMConverterNode
    from agent.nodes.builder_node import LLMProjectBuilderNode
    from agent.nodes.integration_node import LLMIntegrationNode
    from agent.state import ConversionState  # ensure import

    # ✅ use ConversionState, not StateGraph
    graph = StateGraph(ConversionState)

    planner = LLMPlannerNode(client)
    discovery = LLMDiscoveryNode(client)
    converter = LLMConverterNode(client)
    builder = LLMProjectBuilderNode()
    integrator = LLMIntegrationNode(client)

    graph.add_node("planner", planner)
    graph.add_node("discovery", discovery)
    graph.add_node("converter", converter)
    graph.add_node("builder", builder)
    graph.add_node("integrator", integrator)

    # ✅ modern LangGraph API
    graph.set_entry_point("planner")  # instead of set_entry()

    graph.add_edge("planner", "discovery")
    graph.add_edge("discovery", "converter")
    graph.add_edge("converter", "builder")
    graph.add_edge("builder", "integrator")

    return graph


def run_conversion_pipeline(input_dir: str, output_dir: str, log_path=None):
    """Запуск конверсії Rails → Django через LangGraph."""
    from agent.nodes.executor_node import ExecutorNode  # імпорт сюди, щоб уникнути циклу

    client = OpenAI()
    state = ConversionState(input_dir=input_dir, output_dir=output_dir)
    logging.info("🚀 Building conversion graph...")

    executor = ExecutorNode(client, build_graph_func=build_conversion_graph)
    result = executor.run(state)

    logging.info("✅ Conversion complete.")
    return result
