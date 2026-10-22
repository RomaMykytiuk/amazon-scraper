import requests

print("Програма запустилася!")

url = "https://www.amazon.com/s"

params = {
    "k": "computer mouse"
}

try:
    print("Відправляємо запит до Amazon...")

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    print("Статус:", response.status_code)
    print("Розмір HTML:", len(response.text))

    with open("amazon_search.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    print("HTML записано у файл!")

except requests.exceptions.RequestException as error:
    print("Помилка:", error)