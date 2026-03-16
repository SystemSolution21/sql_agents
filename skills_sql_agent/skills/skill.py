# skills.py

# Import built-in libraries
from logging import Logger
from pathlib import Path
from typing import Callable, TypedDict

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage

# Import langchain libraries
from langchain.tools import tool

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
def load_skill(skill_name: str) -> str:
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
            return f"Loaded skill: {skill_name}\n\n{skill['content']}"

    # Skill not found
    available = ", ".join(s["name"] for s in SKILLS)
    return f"Skill '{skill_name}' not found. Available skills: {available}"


class SkillMiddleware(AgentMiddleware):
    """Middleware that injects skill descriptions into the system prompt."""

    # Register the load_skill tool as a class variable
    tools = [load_skill]

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
