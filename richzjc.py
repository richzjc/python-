from richzjcGateIo import *

def requestBiCode():
    url = "https://api.gateio.ws/api/v4/futures/usdt/contracts"
    res = requests.get(url)
    lines = []
    if res.status_code == 200:
        lines = json.loads(res.text)
    realCodes = []
    for value in lines:
        realCodes.append(value["name"])
    setBiCodes(realCodes)
    realLoadCodes()


if __name__ == '__main__':
    requestBiCode()