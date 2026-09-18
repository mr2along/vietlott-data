from datetime import datetime
from typing import Dict, List

from bs4 import BeautifulSoup

from vietlott.crawler.products.base import BaseProduct
from vietlott.crawler.schema.requests import RequestPower655


class ProductPower655(BaseProduct):
    name = "power_655"
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game655CompareWebPart,Vietlott.PlugIn.WebParts.ashx"
    page_to_run = 1  # roll every 2 days

    stored_data_dtype = {
        "date": str,
        "id": str,
        "result": "list",
        "process_time": str,
    }

    org_body = RequestPower655(
        ORenderInfo=BaseProduct.orender_info_default,
        Key="23bbd667",
        GameDrawId="",
        ArrayNumbers=[["" for _ in range(18)] for _ in range(5)],
        CheckMulti=False,
        PageIndex=0,
    )
    org_params = {}

    def __init__(self):
        super(ProductPower655, self).__init__()

    def process_result(self, params, body, res_json, task_data) -> List[Dict]:
        """
        process 645/655 result
        :param params:
        :param body:
        :param res_json:
        :param task_data:
        :return: list of dict data {date, id, result, process_time}
        """
        html = res_json.get("value", {}).get("HtmlContent")
        if not html:
            raise ValueError("Power 6/55 response does not contain HtmlContent")
        soup = BeautifulSoup(html, "lxml")
        data = []
        for i, tr in enumerate(soup.select("table tr")):
            if i == 0:
                continue
            tds = tr.find_all("td")
            row = {}

            row["date"] = datetime.strptime(tds[0].text, "%d/%m/%Y").strftime("%Y-%m-%d")
            row["id"] = tds[1].text

            # last number of special
            row["result"] = [int(span.text) for span in tds[2].find_all("span") if span.text.strip() != "|"]
            if len(row["result"]) != 7:
                raise ValueError(f"Power 6/55 row {row['id']} has {len(row['result'])} numbers")
            if len(set(row["result"][:6])) != 6:
                raise ValueError(f"Power 6/55 row {row['id']} has duplicate main numbers")
            if row["result"][6] in row["result"][:6]:
                raise ValueError(f"Power 6/55 row {row['id']} repeats the special number in the main six")
            row["process_time"] = datetime.now().isoformat()
            data.append(row)
        return data
