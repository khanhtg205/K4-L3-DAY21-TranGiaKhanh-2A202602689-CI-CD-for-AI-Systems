from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import sklearn
import sklearn._loss
import sklearn._loss._loss
from sklearn.ensemble import GradientBoostingClassifier
import joblib
import os
import sys

sys.modules["_loss"] = sklearn._loss._loss

app = FastAPI()

ARTIFACT_BUCKET = os.environ["ARTIFACT_BUCKET"]
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu cloud storage ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import. Su dung
    GOOGLE_APPLICATION_CREDENTIALS de xac thuc (duoc dat trong systemd service).
    """
    # TODO 1: Tao storage.Client()
    client = storage.Client()

    # TODO 2: Lay bucket va blob tuong ung
    bucket = client.bucket(ARTIFACT_BUCKET)
    blob = bucket.blob(MODEL_KEY)

    # TODO 3: Tai file model xuong may
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    blob.download_to_filename(MODEL_PATH)

    # TODO 4: In thong bao thanh cong
    print("Model da duoc tai xuong tu cloud storage.")


download_model()
model = joblib.load(MODEL_PATH)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Must provide exactly 10 features")

    pred = int(model.predict([req.features])[0])
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"
    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
