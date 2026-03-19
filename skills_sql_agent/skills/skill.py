# skills.py

# Import built-in libraries
from logging import Logger
from pathlib import Path
from typing import Callable, NotRequired, TypedDict

# Import langchain libraries
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.messages import SystemMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

# Import local modules
from src.utils.logger import SkillAgentLog

# Initialize logger
logger: Logger = SkillAgentLog.get_logger(module_name=__name__)


def load_skill_content(skill_name: str) -> str:
    """Load skill content from the skill.md file."""
    skill_path: Path = Path(__file__).parent / skill_name / "skill.md"
    try:
        return skill_path.read_text()
    except FileNotFoundError:
        logger.error(msg=f"Skill file not found: {skill_path}")
        return ""


class Skill(TypedDict):
    """A skill that can be progressively disclosed to the agent."""

    name: str  # Unique identifier for the skill
    description: str  # 1-2 sentence description to show in system prompt
    content: str  # Full skill content with detailed instructions


# Define skills
SKILLS: list[Skill] = [
    {
        "name": "sales_analytics",
        "description": "Database schema and business logic for sales data analysis including customers, orders, and revenue.",
        "content": load_skill_content(skill_name="sales_analytics"),
    },
    {
        "name": "inventory_management",
        "description": "Database schema and business logic for inventory tracking including products, warehouses, and stock levels.",
        "content": load_skill_content(skill_name="inventory_management"),
    },
]


# Create skills loading tool
@tool
def load_skill(skill_name: str, runtime: ToolRuntime) -> Command:
    """Load the full content of a skill into the agent's context.

    Use this when you need detailed information about how to handle a specific
    type of request. This will provide you with comprehensive instructions,
    policies, and guidelines for the skill area.

    Args:
        skill_name: The name of the skill to load (e.g., "expense_reporting", "travel_booking")
    """
    # Find and return the requested skill
    for skill in SKILLS:
        if skill["name"] == skill_name:
            skill_content: str = f"Loaded skill: {skill_name}\n\n{skill['content']}"

            # Update state to track loaded skill
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=skill_content,
                            tool_call_id=runtime.tool_call_id,
                        )
                    ],
                    "skills_loaded": [skill_name],
                }
            )

    # Skill not found
    available: str = ", ".join(s["name"] for s in SKILLS)
    content: str = f"Skill '{skill_name}' not found. Available skills: {available}"
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=content,
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


# Create SQL query writing tool
@tool
def write_sql_query(
    query: str,
    vertical: str,
    runtime: ToolRuntime,
) -> str:
    """Write and validate a SQL query for a specific business vertical.

    This tool helps format and validate SQL queries. You must load the
    appropriate skill first to understand the database schema.

    Args:
        query: The SQL query to write
        vertical: The business vertical (sales_analytics or inventory_management)
    """
    # Check if the required skill has been loaded
    skills_loaded = runtime.state.get("skills_loaded", [])

    if vertical not in skills_loaded:
        return (
            f"Error: You must load the '{vertical}' skill first "
            f"to understand the database schema before writing queries. "
            f"Use load_skill('{vertical}') to load the schema."
        )

    # Validate and format the query
    return (
        f"SQL Query for {vertical}:\n\n"
        f"```sql\n{query}\n```\n\n"
        f"✓ Query validated against {vertical} schema\n"
        f"Ready to execute against the database."
    )


class CustomState(AgentState):
    """Custom agent state to track loaded skills."""

    skills_loaded: NotRequired[list[str]]  # Track which skills have been loaded


class SkillMiddleware(AgentMiddleware[CustomState]):
    """Middleware that injects skill descriptions into the system prompt."""

    state_schema = CustomState  # Register the custom agent state to track loaded skills
    tools = [load_skill, write_sql_query]  # Register the tools

    def __init__(self):
        """Initialize and generate the skills prompt from SKILLS."""
        # Build skills prompt from the SKILLS list
        skills_list = []
        for skill in SKILLS:
            skills_list.append(f"- **{skill['name']}**: {skill['description']}")
        self.skills_prompt = "\n".join(skills_list)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Sync: Inject skill descriptions into system prompt."""
        if request.system_message is None:
            return handler(request)

        # Build the skills addendum
        skills_addendum = (
            f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
            "Use the load_skill tool when you need detailed information "
            "about handling a specific type of request."
        )

        # Append to system message content
        new_content = list(request.system_message.content) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)  # type: ignore
        modified_request = request.override(system_message=new_system_message)
        return handler(modified_request)
