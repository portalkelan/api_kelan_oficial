import httpx
import asyncio
import time

async def fetch_message():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post('https://kelanapi.azurewebsites.net/message/question')
            response.raise_for_status()  # Lança um erro se a resposta não for bem-sucedida
            print(response)
            data = response.json()
            print(data)  # Imprime o resultado da API
        except httpx.HTTPError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            print(f"Error message: {exc}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

async def main():
    while True:
        await fetch_message()
        print('Hello World')
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
