# app.py

# Import built-in libraries
import asyncio
import os
import sys
import uuid
from logging import Logger
from pathlib import Path

# Import third-party libraries
from dotenv import load_dotenv

# Import langchain libraries
from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

# Add skills directory to system path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import local modules
from skills.skill import SkillMiddleware
from utils.logger import SkillAgentLog

# Load environment variables
load_dotenv()

# Initialize logger
logger: Logger = SkillAgentLog.get_logger(module_name=__name__)

# Get environment variables
GOOGLE_API_KEY: str | None = os.getenv(key="GOOGLE_API_KEY", default=None)
LLM_MODEL: str = os.getenv(key="LLM_MODEL", default="google_genai:gemini-2.5-flash")

# Initialize model
model: BaseChatModel = init_chat_model(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY)


# Create the agent with skill support
agent = create_agent(
    model,
    system_prompt=(
        "You are a SQL query assistant that helps users "
        "write queries against business databases."
    ),
    middleware=[SkillMiddleware()],
    checkpointer=InMemorySaver(),
)


def main() -> None:
    """Main function to run the SQL agent."""

    # Configuration for this conversation thread
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            # User Query
            query: str = input("Type 'exit' to quit the conversation!\nYou: ").strip()

            if not query:
                continue

            if query.lower() == "exit":
                logger.info(msg="User exited conversation!")
                print("Exiting...")
                break

            # Initialize final message
            final_message = None

            # Stream agent response
            for step in agent.stream(
                input={"messages": [{"role": "user", "content": query}]},
                config=config,
                stream_mode="values",
            ):
                # Print step
                step["messages"][-1].pretty_print()

                # Update final message
                final_message = step["messages"][-1]

            # Print final message
            if final_message and hasattr(final_message, "content"):
                if isinstance(final_message.content, list):
                    for item in final_message.content:
                        if item.get("type") == "text":
                            print(f"\nFinal Answer: {item['text']}")
                            logger.info(
                                msg=f"SQL Agent retrieved final answer successfully: {item['text'][:50]} ..."
                            )
                else:
                    print(f"\nFinal Answer: {final_message.content}")

        except KeyboardInterrupt, EOFError, asyncio.CancelledError:
            logger.info(msg="Keyboard interrupt or EOF error!")
            print("Exiting...")
            break

        except Exception as e:
            logger.error(msg=f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
