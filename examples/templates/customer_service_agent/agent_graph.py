"""Customer Service Agent - Framework-integrated graph definition."""

import os
from framework.graph import EdgeSpec, EdgeCondition, Goal, SuccessCriterion, Constraint
from framework.graph.edge import GraphSpec
from framework.llm import LiteLLMProvider
from framework.runtime.agent_runtime import create_agent_runtime
from framework.runtime.execution_stream import EntryPointSpec

from .nodes import intake, classify, handle, satisfaction

# Define the goal for the agent
goal = Goal(
    id="customer-service-resolution",
    name="Customer Service Resolution",
    description="Resolve customer inquiries with intelligent classification and empathetic responses",
    success_criteria=[
        SuccessCriterion(
            id="issue-classification",
            description="Correctly classify customer issue",
            metric="classification_accuracy",
            target=">=0.8",
            weight=0.4,
        ),
        SuccessCriterion(
            id="customer-satisfaction",
            description="Customer is satisfied with the response",
            metric="sentiment_score",
            target=">0.5",
            weight=0.4,
        ),
        SuccessCriterion(
            id="response-quality",
            description="Response is helpful and empathetic",
            metric="response_quality",
            target=">=0.8",
            weight=0.2,
        ),
    ],
    constraints=[
        Constraint(
            id="empathy-required",
            description="All responses must be empathetic and customer-focused",
            constraint_type="quality",
            category="tone",
        ),
        Constraint(
            id="accuracy-required",
            description="Classifications must be accurate",
            constraint_type="quality",
            category="accuracy",
        ),
    ],
)

# Define workflow nodes
nodes = [
    intake.intake_node,
    classify.classify_node,
    handle.handle_node,
    satisfaction.track_satisfaction_node,
]

# Define edges (workflow connections)
edges = [
    EdgeSpec(
        id="intake-to-classify",
        source="intake",
        target="classify",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    EdgeSpec(
        id="classify-to-handle",
        source="classify",
        target="handle",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
    EdgeSpec(
        id="handle-to-satisfaction",
        source="handle",
        target="satisfaction",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    ),
]

# Graph configuration
entry_node = "intake"
entry_points = {"start": EntryPointSpec(node="intake", input_key="customer_message")}
pause_nodes = []
terminal_nodes = ["satisfaction"]


def create_customer_service_agent_graph():
    """Create and return the customer service agent graph specification."""

    # Get model from environment
    model_name = os.getenv("AGENT_MODEL", "groq/llama-3.1-70b-versatile")

    graph = GraphSpec(
        id="customer-service-agent",
        goal_id=goal.id,
        version="1.0.0",
        entry_node=entry_node,
        entry_points=entry_points,
        terminal_nodes=terminal_nodes,
        pause_nodes=pause_nodes,
        nodes=nodes,
        edges=edges,
        default_model=model_name,
        max_tokens=1000,
        loop_config={
            "max_iterations": 5,
            "max_tool_calls_per_turn": 10,
            "max_history_tokens": 4000,
        },
    )
    return graph


def create_customer_service_agent():
    """Create a customer service agent with framework integration."""

    # Initialize LLM provider
    model_name = os.getenv("AGENT_MODEL", "groq/llama-3.1-70b-versatile")
    llm_provider = None

    try:
        llm_provider = LiteLLMProvider(model=model_name)
    except Exception as e:
        import logging

        logging.warning(f"Failed to initialize LLM provider: {e}")

    # Create graph
    graph = create_customer_service_agent_graph()

    # Create runtime
    try:
        agent_runtime = create_agent_runtime(
            graph=graph,
            llm_provider=llm_provider,
        )
        return agent_runtime
    except Exception as e:
        import logging

        logging.error(f"Failed to create agent runtime: {e}")
        raise


if __name__ == "__main__":
    agent = create_customer_service_agent()
    print(f"Agent created successfully: {agent}")
