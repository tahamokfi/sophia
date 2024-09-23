# import libraries
import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
from llama_index.core import StorageContext
from llama_index.core import SummaryIndex
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector

def rag_query_engine(transcript_text):
    # add openAI API key from the bash environment
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
    # set the models in settings
    Settings.llm = OpenAI(model="gpt-4o")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.chunk_size = 1024

    # Remove the hardcoded test string
    # transcript_text = "hello this is a test for the RAg and this is the second line of the test"
    transcript_doc = Document(text=transcript_text)
    nodes = Settings.node_parser.get_nodes_from_documents([transcript_doc])

    # initialize storage context (by default it's in-memory)
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    # intialize the vector and summary index
    summary_index = SummaryIndex(nodes, storage_context=storage_context)
    vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

    # define the rag query engine
    list_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    vector_query_engine = vector_index.as_query_engine()

    # define the rag query engine
    list_tool = QueryEngineTool.from_defaults(
        query_engine=list_query_engine,
        description=(
            "Useful for summarization questions related to Paul Graham eassy on"
            " What I Worked On."
        ),
    )

    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        description=(
            "Useful for retrieving specific context from Paul Graham essay on What"
            " I Worked On."
        ),
    )

    # create the router query engine
    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            list_tool,
            vector_tool,
        ],
    )

    return query_engine