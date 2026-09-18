from datetime import datetime
from typing import Dict, List

from bs4 import BeautifulSoup
import re
import requests
from loguru import logger

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

    FALLBACK_URL = "https://www.minhngoc.net/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html"

    def crawl_fallback(self, run_date_str: str, index_from: int, index_to: int) -> bool:
        """Use a validated public HTML mirror for daily refresh when Vietlott returns HTTP 403."""
        if index_from != 0:
            raise RuntimeError("Power 6/55 fallback supports only index_from=0")
        logger.warning(f"using Power 6/55 fallback source: {self.FALLBACK_URL}")
        res = requests.get(
            self.FALLBACK_URL,
            headers={"User-Agent": "Mozilla/5.0 (compatible; vietlott-data/0.2)"},
            timeout=15,
        )
        res.raise_for_status()
        text = BeautifulSoup(res.text, "lxml").get_text(" ", strip=True)
        pattern = re.compile(
            r"KẾT QUẢ XỔ SỐ POWER 6/55\s*-\s*NGÀY:\s*(\d{2}/\d{2}/\d{4}).*?"
            r"Kỳ vé:\s*#?(\d{5}).*?Ngày quay thưởng\s*\d{2}/\d{2}/\d{4}\s*(.*?)Giải thưởng",
            re.IGNORECASE,
        )
        rows: List[Dict] = []
        for match in pattern.finditer(text):
            date_str, draw_id, body = match.groups()
            numbers = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", body)]
            if len(numbers) < 7:
                continue
            result = numbers[:7]
            if len(set(result[:6])) != 6 or result[6] in result[:6]:
                continue
            rows.append({
                "date": datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d"),
                "id": draw_id,
                "result": result,
                "process_time": datetime.now().isoformat(),
                "source": self.FALLBACK_URL,
            })
        rows = list({row["id"]: row for row in rows}.values())
        rows.sort(key=lambda row: (row["date"], row["id"]))
        if not rows:
            raise RuntimeError("Power 6/55 fallback returned no validated draws")
        logger.info(f"fallback parsed {len(rows)} Power 6/55 draws, latest={rows[-1]['id']}")
        self._store_fallback_rows(rows)
        return True

    def _store_fallback_rows(self, rows: List[Dict]) -> None:
        import polars as pl
        current_count = 0
        if self.product_config.raw_path.exists():
            current = pl.read_ndjson(self.product_config.raw_path).with_columns(
                pl.col("id").cast(pl.Utf8), pl.col("date").cast(pl.Utf8)
            )
            current_count = len(current)
            existing_ids = set(current["id"].to_list())
            incoming = pl.DataFrame(rows).filter(~pl.col("id").is_in(existing_ids))
            final = pl.concat([current, incoming], how="diagonal_relaxed")
        else:
            final = pl.DataFrame(rows)
        final = final.sort(["date", "id"])
        logger.info(
            f"fallback final min_date={final['date'].min()}, max_date={final['date'].max()}, "
            f"records={current_count}->{len(final)}, diff={len(final) - current_count}"
        )
        final.write_ndjson(self.product_config.raw_path.absolute())

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
