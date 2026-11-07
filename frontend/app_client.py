import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

"""
Method created by Meet Gandhi on 30/01/2024 to check whether the backend is available or not. 
It sends a GET request to the /health endpoint of the backend API and returns the response. 
"""
def check_backend():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout = 5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"status": "unavailable",
                "message": str(e)}


def get_patient_records(patient_id="001"):
    """
    Retrieve all health records for a patient.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}/records/{patient_id}",
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        return {
            "status": "error",
            "message": str(error),
            "records": []
        }

def transcribe_audio(audio_file, language):
    try:
        files = {
            "audio": (
                audio_file.name,
                audio_file.getvalue(),
                audio_file.type or "audio/wav"
            )
        }

        params = {
            "language": language
        }

        response = requests.post(
            f"{API_BASE_URL}/transcribe", 
            files=files, 
            params=params, 
            timeout=600
            )

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "status": "error", 
            "message": str(e)
            }