from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

class LangChainSQLManager:
    def __init__(
        self,
        db_type=LOCALDB,
        sqlite_file="inventers.db",
        mysql_host=None,
        mysql_user=None,
        mysql_password=None,
        mysql_db=None,
    ):
        """
        Initialize the manager and connect to the database.
        """
        self.db_type = db_type
        self.sqlite_file = sqlite_file
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.db = self._configure_db()

    def _configure_db(self):
        """
        Returns a LangChain SQLDatabase object for the selected database.
        """
        if self.db_type == LOCALDB:
            dbfilepath = (Path(__file__).parent / "inventers.db").absolute()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=rw", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        elif self.db_type == MYSQL:
            if not (self.mysql_host and self.mysql_user and self.mysql_password and self.mysql_db):
                raise ValueError("Please provide all MySQL connection details.")
            return SQLDatabase(
                create_engine(
                    f"mysql+mysqlconnector://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}/{self.mysql_db}"
                )
            )
        else:
            raise ValueError("Unknown DB type")

    def run_select_query(self, query: str):
        """
        Runs a SELECT query and returns the result as a list of dicts.
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(query)
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def run_modify_query(self, query: str):
        """
        Runs an INSERT/UPDATE/DELETE query and commits the change.
        Returns the number of affected rows.
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(query)
            conn.commit()
            return result.rowcount

    def get_sql_agent(self, llm, verbose=False):
        """
        Returns a LangChain SQL agent for LLM-powered querying.
        Pass your LLM as the argument.
        """
        toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=verbose,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )
        return agent

# Example usage in another file:
# from your_module import LangChainSQLManager
# db_manager = LangChainSQLManager(db_type="USE_LOCALDB", sqlite_file="inventers.db")
# results = db_manager.run_select_query("SELECT * FROM DEPARTMENT")
# agent = db_manager.get_sql_agent(llm)
