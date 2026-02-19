import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, status

from schemas import AppealCreate

app = FastAPI(title="Сервис обращений абонентов")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


@app.post("/appeals", status_code=status.HTTP_201_CREATED)
async def create_appeal(appeal: AppealCreate) -> dict:
    appeal_id = str(uuid4())

    appeal_data = {
        "id": appeal_id,
        **appeal.model_dump(),
    }

    filepath = DATA_DIR / f"appeal_{appeal_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(appeal_data, f, ensure_ascii=False, indent=2, cls=CustomEncoder)

    return {
        "status": "success",
        "message": "Обращение принято",
        "appeal_id": appeal_id,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
