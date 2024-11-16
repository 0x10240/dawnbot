import httpx
from typing import Tuple

class CapsolverImageSolver:
    BASE_URL = "https://api.capsolver.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10)

    async def solve(self, image: str, module: str = "queueit") -> Tuple[str, bool]:
        """
        Solve a CAPTCHA image using capsolver.

        Args:
            image (str): Base64-encoded image content (without `data:image/*;base64,` prefix).
            module (str): OCR module to use for solving.

        Returns:
            Tuple[str, bool]: The solved text and a boolean indicating success or failure.
        """
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "module": module,
                    "body": image,
                },
            }

            resp = await self.client.post(
                f"{self.BASE_URL}/createTask", json=captcha_data
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                solution = data.get("solution", {}).get("text", "")
                return solution, True

            return data.get("errorDescription", "Unknown error"), False

        except httpx.HTTPStatusError as err:
            return f"HTTP error occurred: {err}", False
        except Exception as err:
            return f"An unexpected error occurred: {err}", False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

