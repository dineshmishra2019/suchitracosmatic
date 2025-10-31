import os
from typing import List, Dict, TypedDict

from django.conf import settings
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

# Ensure the Django environment is set up
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suchitra_cosmatics.settings")
import django
django.setup()

from store.models import Product

### --- Graph State --- ###
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: The user's question.
        generation: The LLM's generated response.
        documents: A list of retrieved documents (products).
    """
    question: str
    generation: str
    documents: List[str]


### --- RAG Nodes --- ###

def retrieve(state: GraphState) -> GraphState:
    """
    Retrieves product information from the database based on the user's question.

    Args:
        state: The current graph state.

    Returns:
        The updated state with retrieved documents.
    """
    print("---RETRIEVING DOCUMENTS---")
    question = state["question"]
    
    # Simple keyword search using Django ORM
    # For a more advanced search, consider using django.contrib.postgres.search
    # or a dedicated search library like Elasticsearch or a vector database.
    keywords = question.split()
    products = Product.objects.none()
    for keyword in keywords:
        products |= Product.objects.filter(name__icontains=keyword) | Product.objects.filter(description__icontains=keyword)

    products = products.distinct()

    documents = []
    for product in products[:5]: # Limit to 5 products
        doc = f"Product Name: {product.name}\nDescription: {product.description}\nPrice: ${product.price}"
        documents.append(doc)
    
    print(f"---FOUND {len(documents)} DOCUMENTS---")
    return {"documents": documents, "question": question}

def generate(state: GraphState) -> GraphState:
    """
    Generates a response using the LLM based on the retrieved documents and question.

    Args:
        state: The current graph state.

    Returns:
        The updated state with the generated response.
    """
    print("---GENERATING RESPONSE---")
    question = state["question"]
    documents = state["documents"]

    prompt = PromptTemplate(
        template="""You are an assistant for an e-commerce website called 'Suchitra Cosmetics'.
        Use the following retrieved context to answer the user's question.
        If you don't know the answer, just say that you don't have information about it.
        Be concise and helpful.

        Question: {question}
        Context: {context}
        Answer:""",
        input_variables=["question", "context"],
    )

    llm = ChatOllama(model="llama3", temperature=0)
    rag_chain = prompt | llm | StrOutputParser()

    generation = rag_chain.invoke({"context": "\n\n".join(documents), "question": question})
    print("---GENERATED RESPONSE---")
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state: GraphState) -> GraphState:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state: The current graph state.

    Returns:
        The original state, with a "grade" added to the documents list.
    """
    print("---CHECKING DOCUMENT RELEVANCE---")
    question = state["question"]
    documents = state["documents"]

    llm = ChatOllama(model="llama3", format="json", temperature=0)

    prompt = PromptTemplate(
        template="""You are a grader assessing the relevance of a retrieved document to a user question.
        If the document contains keywords related to the user question, grade it as relevant.
        Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question.
        Provide the binary score as a JSON with a single key 'score'.

        Retrieved document: \n\n {document} \n\n
        User question: {question}""",
        input_variables=["question", "document"],
    )

    chain = prompt | llm | JsonOutputParser()
    
    graded_documents = []
    for doc in documents:
        score = chain.invoke({"question": question, "document": doc})
        if score.get("score") == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            graded_documents.append(doc)
    
    return {"documents": graded_documents, "question": question}

def decide_to_generate(state: GraphState) -> str:
    """
    Determines whether to generate a response or end the process.
    """
    print("---ASSESSING GRADED DOCUMENTS---")
    if not state["documents"]:
        print("---DECISION: NO RELEVANT DOCUMENTS, ENDING---")
        return "end"
    else:
        print("---DECISION: RELEVANT DOCUMENTS FOUND, GENERATING---")
        return "generate"


# Build the graph
workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "generate": "generate",
        "end": END,
    },
)
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("generate", END)
workflow.set_entry_point("retrieve")

rag_app = workflow.compile()

# To test the chain directly:
# if __name__ == "__main__":
#     inputs = {"question": "do you have any red lipstick?"}
#     for output in rag_app.stream(inputs):
#         for key, value in output.items():
#             print(f"Node '{key}':")
#         print("\n---\n")
#     print(output['generate']['generation'])