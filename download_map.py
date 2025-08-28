import requests

url = "https://www.shutterstock.com/image-vector/dominican-republic-political-map-capital-santo-260nw-1922633543.jpg"
response = requests.get(url)

with open("mapa_rd.jpg", "wb") as f:
    f.write(response.content)