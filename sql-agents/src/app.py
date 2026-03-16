# Import built-in libraries
import asyncio
import os
from logging import Logger

# Import local libraries
from database import db

# Import dotenv libraries
from dotenv import load_dotenv

# Import langchain libraries
from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from utils.logger import SqlAgentLog

# Load environment variables
load_dotenv()

# Initialize logger
logger: Logger = SqlAgentLog.get_logger(module_name=__name__)

# Get environment variables
GOOGLE_API_KEY: str | None = os.getenv(key="GOOGLE_API_KEY", default=None)
LLM_MODEL: str = os.getenv(key="LLM_MODEL", default="google_genai:gemini-2.5-flash")

# Initialize model
model: BaseChatModel = init_chat_model(model=LLM_MODEL, google_api_key=GOOGLE_API_KEY)

# Initialize Tools
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

for tool in tools:
    print(f"{tool.name}: {tool.description}\n")


# Agent System Prompt
system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

# Create agent
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


def main() -> None:
    """
    Main function to run the SQL agent.
    """

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
                {"messages": [{"role": "user", "content": query}]},
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
