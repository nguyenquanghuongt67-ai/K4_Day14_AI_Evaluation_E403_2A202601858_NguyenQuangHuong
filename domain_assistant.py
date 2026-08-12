import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.prebuilt import create_react_agent

# Load Template classes for Live RAGAS Metrics
from template import RAGASEvaluator, QAPair

load_dotenv()

app = FastAPI(title="OrbitTech Agent API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db_v2", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 1. KHAI BÁO TOOL & RAG RETRIEVER
@tool
def search_orbit_tech_kb(query: str) -> str:
    """Tìm kiếm cơ sở dữ liệu tri thức của cửa hàng OrbitTech để lấy thông tin về chính sách, bảo hành, sản phẩm và đổi trả."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

tools = [search_orbit_tech_kb]

# Initialize LLM
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in .env")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model_name=OPENROUTER_MODEL,
    temperature=0.0,
    max_tokens=2000
)

# 2. THIẾT KẾ SYSTEM PROMPT CHỐNG HALLUCINATION
system_prompt = """Bạn là chuyên viên tư vấn khách hàng chuyên nghiệp của cửa hàng công nghệ OrbitTech.
Tone & Voice: Lịch sự, ngắn gọn, thân thiện, LUÔN LUÔN trả lời bằng tiếng Việt.

Quy tắc nghiêm ngặt:
1. Bạn CẦN dùng tool `search_orbit_tech_kb` để tra cứu thông tin OrbitTech trước khi trả lời.
2. CHỈ sử dụng thông tin trong Retrieved Context để trả lời. Không sử dụng kiến thức bên ngoài.
3. Nếu câu hỏi chỉ là chào hỏi (ví dụ: "xin chào", "hi"), hãy trả lời lịch sự và hỏi xem có thể hỗ trợ gì về sản phẩm/chính sách OrbitTech.
4. Nếu thông tin không có trong Context, TUYỆT ĐỐI không tự bịa (Hallucination). Hãy trả lời chính xác câu này: "Thật xin lỗi, tôi chưa có thông tin chi tiết về vấn đề này trong cơ sở dữ liệu của OrbitTech."
5. Hãy tóm tắt câu trả lời một cách mạch lạc và dễ hiểu nhất.

Câu hỏi của khách hàng: {input}
"""

# 3. AGENT EXECUTION
agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Run agent
        response = agent_executor.invoke({"messages": [("user", req.question)]})
        answer = response["messages"][-1].content
        
        # Lấy trực tiếp chunk scores để gửi xuống ReactJS render lên Micro-Cards
        docs_with_scores = vectorstore.similarity_search_with_score(req.question, k=3)
        contexts = [{"text": d[0].page_content, "score": float(d[1])} for d in docs_with_scores]
        context_texts = [d.page_content for d, _ in docs_with_scores]
        
        # Calculate RAGAS Metrics
        qapair = QAPair(
            question=req.question,
            expected_answer=answer, 
            context=" ".join(context_texts),
            retrieved_contexts=context_texts
        )
        qapair.actual_answer = answer
        
        evaluator = RAGASEvaluator()
        eval_res = evaluator.run_full_eval(
            answer=qapair.actual_answer,
            question=qapair.question,
            context=qapair.context,
            expected=qapair.expected_answer,
            contexts=qapair.retrieved_contexts
        )
        
        metrics = {
            "faithfulness": eval_res.faithfulness,
            "relevance": eval_res.answer_relevance,
            "completeness": eval_res.completeness,
            "recall": eval_res.context_recall if eval_res.context_recall is not None else 0.0,
            "precision": eval_res.context_precision if eval_res.context_precision is not None else 0.0,
        }
        
        return {
            "answer": answer,
            "contexts": contexts,
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Bắt lỗi Try-Catch chi tiết trả về React UI
        return {
            "answer": "Thật xin lỗi, hệ thống đang gặp sự cố kết nối tới AI. Vui lòng thử lại sau.",
            "error_message": str(e),
            "contexts": [],
            "metrics": {}
        }

if __name__ == "__main__":
    uvicorn.run("domain_assistant:app", host="127.0.0.1", port=8000, reload=True)
