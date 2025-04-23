from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import uvicorn

from t_5_search.searcher import TFIDFVectorSearch

app = FastAPI()
templates = Jinja2Templates(directory="templates")
searchers = TFIDFVectorSearch(data_dir="output_terms")
inverted_index = searchers.load_index()

index_map = {}
file = os.path.join(os.getcwd(), "index.txt")
with open(file, "r", encoding="utf-8") as f:
    for line in f:
        filename, url = line.strip().split()
        num = int(filename.replace(".html", ""))
        index_map[num] = url

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def handle_query(request: Request, query: str = Form(...)):
    if not query.strip():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "query": query,
            "results": [],
            "error": "Пустой запрос. Пожалуйста, введите текст."
        })
    searchers.load_data()
    searchers.save_index()
    results = searchers.search(query, top_k=10)
    top_ids = [doc_data["doc_id"] for doc_data in results[:10]]

    urls = [index_map.get(doc_id) for doc_id in top_ids if doc_id in index_map]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "query": query,
        "results": urls
    })


if __name__ == "__main__":
    uvicorn.run("demo.main:app", host="127.0.0.1", port=8000, reload=True)
    # uvicorn demo.main:app --reload
