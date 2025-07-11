# llmclients.py

from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class GroqLLMClient:
    def __init__(self, groq_api_key, model_name="Llama3-8b-8192", streaming=False):
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name, streaming=streaming)

    def get_response(self, retriever, context, query, system_message=None):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are assistant inventers company. Provideing the Real-time context, Answer accordingly in Short Summery or informatic way.\n\nContext:\n{context}"),
            ("user", "{input}")
        ])
        combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
        result = retrieval_chain.invoke({
            "input": query,
            "context": context
        })
        return result["answer"] if "answer" in result else result

    
    def get_summery_response(self, query,context=''):
        sql_skeleton = '''
            TABLE: CEO
            - CEO_ID       INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(50)
            - EMAIL        VARCHAR(50)

            TABLE: DEPARTMENT
            - DEPT_ID      INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(30)

            TABLE: MANAGER
            - MANAGER_ID   INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(50)
            - DEPT_ID      INTEGER       FOREIGN KEY → DEPARTMENT(DEPT_ID)
            - EMAIL        VARCHAR(50)

            TABLE: EMPLOYEE
            - EMP_ID       INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(50)
            - DEPT_ID      INTEGER       FOREIGN KEY → DEPARTMENT(DEPT_ID)
            - MANAGER_ID   INTEGER       FOREIGN KEY → MANAGER(MANAGER_ID)
            - ROLE         VARCHAR(30)
            - EMAIL        VARCHAR(50)

            TABLE: PROJECT
            - PROJECT_ID   INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(50)
            - DEPT_ID      INTEGER       FOREIGN KEY → DEPARTMENT(DEPT_ID)
            - MANAGER_ID   INTEGER       FOREIGN KEY → MANAGER(MANAGER_ID)
            - STATUS       VARCHAR(20)

            TABLE: TASK
            - TASK_ID      INTEGER       PRIMARY KEY AUTOINCREMENT
            - PROJECT_ID   INTEGER       FOREIGN KEY → PROJECT(PROJECT_ID)
            - NAME         VARCHAR(100)
            - ASSIGNED_TO  INTEGER       FOREIGN KEY → EMPLOYEE(EMP_ID)
            - STATUS       VARCHAR(20)
            - DEADLINE     DATE

            TABLE: INTERVIEW
            - INTERVIEW_ID     INTEGER       PRIMARY KEY AUTOINCREMENT
            - CANDIDATE_NAME   VARCHAR(50)
            - POSITION         VARCHAR(30)
            - HR_ID            INTEGER       FOREIGN KEY → EMPLOYEE(EMP_ID)
            - RESULT           VARCHAR(20)
            - DATE             DATE

            TABLE: CLIENT
            - CLIENT_ID    INTEGER       PRIMARY KEY AUTOINCREMENT
            - NAME         VARCHAR(50)
            - CONTACT      VARCHAR(50)
            - PROJECT_ID   INTEGER       FOREIGN KEY → PROJECT(PROJECT_ID)
            - STATUS       VARCHAR(20)
        '''

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query expert for the Inventurs company.\nHere is the database schema:\n\n{sql_schema}\n\nBased on this, provide the context for quering the langchain sql agent based on the user query:{query} for retriving the data from sql. Provide Short and precise answer. context: {context}"),
        ])

        # Format messages using the template
        messages = prompt.format_messages(sql_schema=sql_skeleton, query=query, context=context)

        # Invoke the LLM directly
        response = self.llm.invoke(messages)
        print(response)

        return response.content



