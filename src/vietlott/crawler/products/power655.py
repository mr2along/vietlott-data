from datetime import datetime, timedelta
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
    FALLBACK_DATE_URL = (
        "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/"
        "power-6x55/{date}.html"
    )
    # Minh Ngoc's date pages expose roughly 10 Power 6/55 draws. The first
    # historical page needed after the current page is anchored about 18 days
    # before the run date; each subsequent page advances by about 23 days.
    FALLBACK_PAGE_ANCHOR_DAYS = 18
    FALLBACK_PAGE_SPAN_DAYS = 23
    # Historical correction metadata is retained for explicit correction/backfill
    # operations only. Daily incremental crawl never reloads an existing draw.
    KNOWN_CORRECTION_ID = "01394"
    KNOWN_CORRECTION_DATE = "2026-09-05"

    _FALLBACK_PATTERN = re.compile(
        r"KẾT QUẢ XỔ SỐ POWER 6/55\s*-\s*NGÀY:\s*(\d{2}/\d{2}/\d{4}).*?"
        r"Kỳ vé:\s*#?(\d{5}).*?"
        r"Ngày quay thưởng\s*(\d{2}/\d{2}/\d{4})\s*(.*?)Giải thưởng",
        re.IGNORECASE,
    )

    def _parse_fallback_text(self, text: str) -> List[Dict]:
        rows: List[Dict] = []
        for match in self._FALLBACK_PATTERN.finditer(text):
            date_str, draw_id, draw_date_str, body = match.groups()
            if date_str != draw_date_str:
                logger.warning(
                    f"discarding fallback row {draw_id}: page date {date_str} "
                    f"does not match draw date {draw_date_str}"
                )
                continue

            numbers = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", body)]
            if len(numbers) < 7:
                continue
            result = numbers[:7]
            if (
                len(set(result[:6])) != 6
                or any(n < 1 or n > 55 for n in result)
                or result[6] in result[:6]
            ):
                continue

            rows.append(
                {
                    "date": datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    "id": draw_id,
                    "result": result,
                    "process_time": datetime.now().isoformat(),
                }
            )
        return rows

    def _fallback_page_urls(
        self, run_date_str: str, index_from: int, index_to: int
    ) -> List[str]:
        if index_from == 0 and index_to <= 1:
            return [self.FALLBACK_URL]

        base_date = datetime.strptime(run_date_str, "%Y-%m-%d").date()
        urls: List[str] = []
        for page_index in range(index_from, index_to):
            if page_index == 0:
                urls.append(self.FALLBACK_URL)
                continue
            offset = self.FALLBACK_PAGE_ANCHOR_DAYS + (
                (page_index - 1) * self.FALLBACK_PAGE_SPAN_DAYS
            )
            anchor = base_date - timedelta(days=offset)
            urls.append(self.FALLBACK_DATE_URL.format(date=anchor.strftime("%d-%m-%Y")))
        return urls

    def crawl_fallback(self, run_date_str: str, index_from: int, index_to: int) -> bool:
        """Use validated public HTML mirror for daily refresh and historical backfill."""
        urls = self._fallback_page_urls(run_date_str, index_from, index_to)
        logger.warning(
            "using Power 6/55 fallback source(s): " + ", ".join(urls)
        )

        rows: List[Dict] = []
        for url in urls:
            res = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; vietlott-data/0.2)"},
                timeout=15,
            )
            res.raise_for_status()
            text = BeautifulSoup(res.text, "lxml").get_text(" ", strip=True)
            page_rows = self._parse_fallback_text(text)
            logger.info(f"fallback parsed {len(page_rows)} Power 6/55 draws from {url}")
            rows.extend(page_rows)

        rows = list({row["id"]: row for row in rows}.values())
        rows.sort(key=lambda row: (row["date"], row["id"]))
        if not rows:
            raise RuntimeError("Power 6/55 fallback returned no validated draws")

        # Only a single-page request [0, 1) is a daily refresh. Multi-page
        # requests are historical backfills and must upsert every validated row.
        # Even on a daily refresh, fill any missing IDs already covered by the
        # latest page before appending at most the next new draw.
        if index_from == 0 and index_to <= 1:
            import polars as pl

            current_ids: set[int] = set()
            if self.product_config.raw_path.exists():
                current = pl.read_ndjson(
                    self.product_config.raw_path, infer_schema_length=None
                ).with_columns(pl.col("id").cast(pl.Utf8))
                current_ids = {int(value) for value in current["id"].to_list()}
            current_max_id = max(current_ids, default=0)

            recoverable_gaps = [
                row
                for row in rows
                if int(row["id"]) < current_max_id and int(row["id"]) not in current_ids
            ]
            new_rows = [row for row in rows if int(row["id"]) > current_max_id]
            next_draw_rows = (
                [min(new_rows, key=lambda row: int(row["id"]))]
                if new_rows
                else []
            )
            rows = recoverable_gaps + next_draw_rows
            if not rows:
                logger.info(
                    f"Power 6/55 already up to date at #{current_max_id:05d}; "
                    "no new draw or recoverable latest-page gap to store."
                )
                return True

            logger.info(
                f"incremental Power 6/55 crawl: current=#{current_max_id:05d}, "
                f"recovering {len(recoverable_gaps)} internal gap(s), "
                f"appending {len(next_draw_rows)} next draw(s)"
            )

        rows = list({row["id"]: row for row in rows}.values())
        rows.sort(key=lambda row: (row["date"], row["id"]))
        logger.info(
            f"fallback selected {len(rows)} draw(s), latest={rows[-1]['id']}"
        )
        self._store_fallback_rows(rows)
        return True

    def _store_fallback_rows(self, rows: List[Dict]) -> None:
        import polars as pl

        current_count = 0
        incoming = pl.DataFrame(rows).with_columns(
            pl.col("id").cast(pl.Utf8),
            pl.col("date").cast(pl.Utf8),
        )

        if self.product_config.raw_path.exists():
            current = pl.read_ndjson(self.product_config.raw_path).with_columns(
                pl.col("id").cast(pl.Utf8),
                pl.col("date").cast(pl.Utf8),
            )
            current_count = len(current)
            incoming_ids = set(incoming["id"].to_list())
            # Upsert by draw id so a prior malformed/stale row can be corrected.
            retained = current.filter(~pl.col("id").is_in(incoming_ids))
            final = pl.concat([retained, incoming], how="diagonal_relaxed")
        else:
            final = incoming

        final = final.unique(subset=["id"], keep="last").sort(["date", "id"])
        logger.info(
            f"fallback final min_date={final['date'].min()}, max_date={final['date'].max()}, "
            f"records={current_count}->{len(final)}, diff={len(final) - current_count}"
        )
        final.write_ndjson(self.product_config.raw_path.absolute())

    def process_result(self, params, body, res_json, task_data) -> List[Dict]:
        """Process official Power 6/55 results."""
        html = res_json.get("value", {}).get("HtmlContent")
        if not html:
            raise ValueError("Power 6/55 response does not contain HtmlContent")
        soup = BeautifulSoup(html, "lxml")
        data = []
        for i, tr in enumerate(soup.select("table tr")):
            if i == 0:
                continue
            tds = tr.find_all("td")
            if len(tds) < 3:
                raise ValueError("Power 6/55 result row is missing required columns")
            row = {}
            row["date"] = datetime.strptime(tds[0].text.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
            row["id"] = tds[1].text.strip()
            row["result"] = [
                int(span.text.strip())
                for span in tds[2].find_all("span")
                if span.text.strip() != "|"
            ]
            if len(row["result"]) != 7:
                raise ValueError(f"Power 6/55 row {row['id']} has {len(row['result'])} numbers")
            if (
                len(set(row["result"][:6])) != 6
                or any(n < 1 or n > 55 for n in row["result"])
                or row["result"][6] in row["result"][:6]
            ):
                raise ValueError(f"Power 6/55 row {row['id']} has an invalid 6+1 result")
            row["process_time"] = datetime.now().isoformat()
            data.append(row)
        return data
