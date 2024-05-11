from operator import itemgetter
from langchain.schema.retriever import BaseRetriever
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.runnable import Runnable, RunnableMap
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from stack.app.utils import format_docs


def create_retriever_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    rephrase_template: str,
    use_chat_history: bool,
) -> Runnable:
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(rephrase_template)
    if not use_chat_history:
        initial_chain = (itemgetter("question")) | retriever
        return initial_chain
    else:
        condense_question_chain = (
            {
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | CONDENSE_QUESTION_PROMPT
            | llm
            | StrOutputParser()
        ).with_config(
            run_name="CondenseQuestion",
        )
        conversation_chain = condense_question_chain | retriever
        return conversation_chain


def create_universal_retrieval_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    response_template: str,
    rephrase_template: str,
    use_chat_history: bool = False,
) -> Runnable:
    retriever_chain = create_retriever_chain(
        llm, retriever, rephrase_template, use_chat_history
    ).with_config(run_name="ChatPipeline")

    _context = RunnableMap(
        {
            "context": retriever_chain | format_docs,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
    ).with_config(run_name="RetrieveDocs")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", response_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    response_synthesizer = (prompt | llm | StrOutputParser()).with_config(
        run_name="GenerateResponse",
    )

    return _context | response_synthesizer
