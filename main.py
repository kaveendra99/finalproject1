from io import BytesIO
import os
import cv2
from time import strftime, time
from threading import Timer
from model import *
from PIL import Image
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKey
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi import FastAPI, HTTPException, status, File, Depends
from error import *
from DETECTION.detection import DETECTION
from DATABASE.sqliteIO import SQLiteIO
from settings import Settings

settings = Settings()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

detection_model = DETECTION(settings=settings)
db = SQLiteIO(
    settings.DATABASE_PATH,
    settings.QUERY_FILE_PATH,
    settings.DATABASE_TYPE,
)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def check_expired_files():
    print(f"DELETE FILES AFTER {settings.RETENTION_PERIOD} MINS")
    id_list = []
    current_time = time()
    for id, file_path in db.get_expired_files(current_time=current_time):
        delete_file(file_path)
        id_list.append({"id": id})
    db.delete_expired_files(id_list)
    Timer(60, check_expired_files).start()


Timer(60, check_expired_files).start()

app = FastAPI(redoc_url=None, docs_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

if settings.CORS_ORIGINS != "":
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_api_key(api_key: APIKey = Depends(api_key_header)):
    available_key = settings.API_KEY
    if available_key is not None:
        return available_key
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Waste Detection and Management API",
        version="1.0.0",
        description="Python based REST API for Waste Detection.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "/static/icon512.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


def save_image_in_static_dir(image) -> tuple:
    file_name = "{}.png".format(strftime("%Y%m%d-%H%M%S"))
    full_path = os.path.join(settings.PREDICTIONS_SAVE_PATH, file_name)
    cv2.imwrite(full_path, img=image)
    return (f"{settings.PREDICTIONS_ACCESS_PATH}/{file_name}", full_path)


@app.get("/", include_in_schema=False)
def read_root():
    html_content = """
    <html>
        <head>
            <title>Waste Detection and Management API</title>
        </head>
        <body>
            <h1>
                <a id="link">Go to Swagger Docs</a>
            </h1>
        </body>
        <script>
            document.getElementById("link").href = window.location.href + "docs";
        </script>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Waste Detection and Management API",
        swagger_favicon_url="/static/icon192.png",
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse("/static/favicon.ico")


@app.post("/detect_img", status_code=200)
async def detect_waste(
    api_key: APIKey = Depends(get_api_key), image_file: bytes = File(...)
) -> ResponseModel:
    detections: list = []
    response = ResponseModel()
    try:
        try:
            input_image = Image.open(BytesIO(image_file)).convert("RGB")
        except:
            raise FileReadError()
        detection_dict = detection_model.detect(input_image, settings)
        (static_file_path, full_file_path) = save_image_in_static_dir(
            detection_dict[settings.IMAGE]
        )
        schedule_time = time() + (settings.RETENTION_PERIOD * 60)
        db.insert_file(full_file_path=full_file_path, schedule_time=schedule_time)
        for idx, conf in enumerate(detection_dict[settings.CONF_LIST]):
            detect = SingleDetectModel()
            detect.confidence = conf * 100
            detect.detected_class = detection_dict[settings.CLS_LIST][idx]
            detect.box_xy_list = detection_dict[settings.DETECT_LIST][idx]
            detections.append(detect)

        # Create Response
        response.imageURL = static_file_path
        response.detections = detections
        resJson = jsonable_encoder(response)
        return JSONResponse(status_code=status.HTTP_200_OK, content=resJson)
    except Exception as e:
        errorMessage = ""
        httpStatus = None

        if isinstance(e, FileReadError):
            errorMessage = e.message
            httpStatus = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        elif isinstance(
            e,
            (),
        ):
            errorMessage = e.message
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            print(e)
            errorMessage = "Unknown Error"
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR

        response.error = errorMessage
        resJson = jsonable_encoder(response)
        return JSONResponse(status_code=httpStatus, content=resJson)
