from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the CSV data into a DataFrame
df = pd.read_csv('cpi_combined_data.csv')

# Define a Pydantic model for the response
class CPIData(BaseModel):
    Date: str
    CPI_All_Items: Optional[float]
    CPI_Less_Food_Energy: Optional[float]
    CPI_Gasoline: Optional[float]

@app.get("/cpi", response_model=List[CPIData])
async def get_cpi_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Fetch CPI data from the CSV file.
    - `start_date` and `end_date` should be in the format 'YYYY-MM-DD'.
    """

    filtered_df = df

    if start_date:
        filtered_df = filtered_df[filtered_df['Date'] >= start_date]
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'] <= end_date]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified date range")

    result = filtered_df.to_dict(orient='records')
    return result

# To run the app, use the command: uvicorn app:app --reload
