from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
import pandas as pd
from ydata_profiling import ProfileReport
import tempfile
import os

app = FastAPI(title="CSV Dataset Report Generator")

@app.post("/generate-report")
async def generate_report(request: Request):
    try:
        # 1️⃣ Read raw CSV bytes
        body = await request.body()

        if not body:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty request body. Please upload a CSV file."}
            )

        # 2️⃣ Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "input.csv")
            html_path = os.path.join(tmpdir, "dataset_report.html")

            # 3️⃣ Save CSV
            with open(csv_path, "wb") as f:
                f.write(body)

            # 4️⃣ Read CSV safely
            df = pd.read_csv(
                csv_path,
                sep=None,
                engine="python",
                encoding="utf-8"
            )

            if df.empty or df.shape[1] == 0:
                return JSONResponse(
                    status_code=400,
                    content={"error": "CSV file is empty or invalid."}
                )

            # 5️⃣ Generate profiling report (SAFE MODE)
            profile = ProfileReport(
                df,
                title="Dataset Profiling Report",
                explorative=True,
                minimal=True,
                correlations=None
            )
            profile.to_file(html_path)

            # 6️⃣ Read HTML into memory
            with open(html_path, "rb") as f:
                html_bytes = f.read()

        # 7️⃣ Return HTML as response (NO temp file issues)
        return Response(
            content=html_bytes,
            media_type="text/html",
            headers={
                "Content-Disposition": "attachment; filename=dataset_report.html"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )
