from pathlib import Path
from pgpt_python.client import PrivateGPTApi

pgpt_client = PrivateGPTApi(base_url="http://localhost:8001")


async def summarize_text(text: str) -> str:
    chunks = split_text_into_chunks(text)
    summaries = []
    try:
        for chunk in chunks:
            response = pgpt_client.contextual_completions.prompt_completion(
                prompt=f"Summarize this document:\n{chunk}"
            )
            summaries.append(response.choices[0].message.content)
        return " ".join(summaries)
    except Exception as e:
        print(f"An error occurred during summarization: {str(e)}")
        summaries.append(f"An error occurred during summarization. {str(e)}")
    return " ".join(summaries)

async def background_summarize(file_path: Path, file_name: str, summaries_store: dict):
    from src.services.file_operations import extract_text_from_pdf
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError("No text extracted from PDF.")
    summary = await summarize_text(text)
    summaries_store[file_name] = {"summary": summary, "status": "completed"}
    print(f"Summary for {file_path.name}: {summary}")
    
def split_text_into_chunks(text: str, chunk_size: int = 2048) -> list:
    """Split text into manageable chunks."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]