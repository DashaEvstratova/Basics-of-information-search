from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from t_5_search.searcher import load_data, search

app = FastAPI()
templates = Jinja2Templates(directory="templates")

inverted_index, idf_dict = load_data()

index_map = {}
with open("demo/index.txt", "r", encoding="utf-8") as f:
    for line in f:
        filename, url = line.strip().split()
        num = int(filename.replace(".html", ""))
        index_map[num] = url


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def handle_query(request: Request, query: str = Form(...)):
    results = search(query, inverted_index, idf_dict)
    top_ids = [doc_id for doc_id, _ in results[:10]]
    urls = [index_map.get(doc_id) for doc_id in top_ids if doc_id in index_map]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "query": query,
        "results": urls
    })


if __name__ == "__main__":
    uvicorn.run("demo.main:app", host="127.0.0.1", port=8000, reload=True)
    # uvicorn demo.main:app --reload
