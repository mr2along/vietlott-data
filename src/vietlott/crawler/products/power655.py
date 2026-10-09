from datetime import datetime
from typing import Dict, List
import re

from bs4 import BeautifulSoup
import requests
from loguru import logger

from vietlott.crawler.products.base import BaseProduct
from vietlott.crawler.schema.requests import RequestPower655


class ProductPower655(BaseProduct):
    name = "power_655"
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game655CompareWebPart,Vietlott.PlugIn.WebParts.ashx"
    page_to_run = 1

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

    # Independent public sources. Minh Ngoc is intentionally not used.
    FALLBACK_URLS = (
        "https://xoso.com.vn/xo-so-power-655.html",
        "https://xskt.com.vn/xspower/200-ngay",
    )
    KNOWN_CORRECTION_ID = "01394"
    KNOWN_CORRECTION_DATE = "2026-09-05"
    REQUEST_TIMEOUT_SECONDS = 20
    USER_AGENT = "Mozilla/5.0 (compatible; vietlott-data/0.3; +https://github.com/mr2along/vietlott-data)"

    _DRAW_MARKER = re.compile(r"(?:Kỳ\s+(?:quay thưởng|mở thưởng)|Kỳ vé)\s*:?\s*#?(\d{5})", re.IGNORECASE)
    _DATE = re.compile(r"(?<!\d)(\d{2}[/-]\d{2}[/-]\d{4})(?!\d)")
    _NUMBER = re.compile(r"(?<!\d)(\d{1,2})(?!\d)")

    def _valid_result(self, result: List[int]) -> bool:
        return (
            len(result) == 7
            and len(set(result[:6])) == 6
            and all(1 <= n <= 55 for n in result)
            and result[6] not in result[:6]
        )

    def _parse_fallback_text(self, text: str, source: str = "unknown") -> List[Dict]:
        """Parse Power 6/55 results from xoso.com.vn or xskt.com.vn text."""
        normalized = re.sub(r"\s+", " ", text).strip()
        markers = list(self._DRAW_MARKER.finditer(normalized))
        rows: List[Dict] = []
        for index, marker in enumerate(markers):
            draw_id = marker.group(1)
            start = marker.end()
            end = markers[index + 1].start() if index + 1 < len(markers) else len(normalized)
            segment = normalized[start:end]

            # The date is printed immediately before the draw ID on both source
            # layouts. Restrict the search window to avoid taking a prior draw's date.
            date_prefix = normalized[max(0, marker.start() - 110):marker.start()]
            date_matches = list(self._DATE.finditer(date_prefix))
            if not date_matches:
                logger.warning("fallback row {} from {} has no date", draw_id, source)
                continue
            date_text = date_matches[-1].group(1).replace("-", "/")
            try:
                draw_date = datetime.strptime(date_text, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                logger.warning("fallback row {} from {} has invalid date {}", draw_id, source, date_text)
                continue

            # Result numbers occur before the prize table / next draw marker.
            # Parse only the first seven number tokens after the draw ID.
            numbers = [int(value) for value in self._NUMBER.findall(segment)]
            result = numbers[:7]
            if not self._valid_result(result):
                logger.warning("fallback row {} from {} has invalid result {}", draw_id, source, result)
                continue
            rows.append({
                "date": draw_date,
                "id": draw_id,
                "result": result,
                "process_time": datetime.now().isoformat(),
                "source": source,
            })
        return rows

    def _fetch_fallback_source(self, url: str) -> List[Dict]:
        response = requests.get(
            url,
            headers={"User-Agent": self.USER_AGENT},
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text(" ", strip=True)
        rows = self._parse_fallback_text(text, source=url.split("/")[2])
        logger.info("Power 6/55 fallback source={} parsed_rows={}", url, len(rows))
        if not rows:
            raise RuntimeError(f"Power 6/55 fallback source returned no validated draws: {url}")
        return rows

    def crawl_fallback(self, run_date_str: str, index_from: int, index_to: int) -> bool:
        """Fetch validated rows from independent sources, never from Minh Ngoc."""
        rows_by_id: Dict[str, Dict] = {}
        failures = []
        for url in self.FALLBACK_URLS:
            try:
                for row in self._fetch_fallback_source(url):
                    # Prefer xoso.com.vn when both sources publish the same draw.
                    rows_by_id.setdefault(row["id"], row)
            except Exception as exc:
                failures.append(f"{url}: {exc}")
                logger.warning("Power 6/55 fallback source failed: {}", failures[-1])

        if not rows_by_id:
            raise RuntimeError("All independent Power 6/55 fallback sources failed: " + "; ".join(failures))

        rows = sorted(rows_by_id.values(), key=lambda row: (row["date"], int(row["id"])))
        import polars as pl

        raw_path = self.product_config.raw_path
        current = pl.read_ndjson(raw_path, infer_schema_length=None) if raw_path.exists() else pl.DataFrame()
        current_ids = set()
        current_max_id = 0
        if current.height and "id" in current.columns:
            current = current.with_columns(pl.col("id").cast(pl.Utf8))
            current_ids = set(current["id"].to_list())
            current_max_id = max(int(value) for value in current["id"].to_list())

        selected: List[Dict] = []
        # Preserve the established operational rule: every crawl refreshes #01394
        # when a validated independent source still exposes it.
        correction = rows_by_id.get(self.KNOWN_CORRECTION_ID)
        if correction is not None:
            selected.append(correction)

        if index_from == 0:
            unseen = [row for row in rows if int(row["id"]) > current_max_id]
            if not current.height:
                # Bootstrap must start at the newest available draw, not the oldest.
                next_rows = [max(rows, key=lambda row: int(row["id"]))]
            elif unseen:
                next_id = min(int(row["id"]) for row in unseen)
                next_rows = [row for row in unseen if int(row["id"]) == next_id]
            else:
                next_rows = []
            selected.extend(next_rows)
        else:
            # Historical source pages are finite; use draw IDs as the stable
            # backfill cursor, with six draws per source-page step.
            low_id = max(1, current_max_id - max(index_to, index_from + 1) * 6)
            high_id = max(1, current_max_id - index_from * 6)
            selected.extend(row for row in rows if low_id <= int(row["id"]) < high_id)

        # Keep only validated rows, deduplicated by draw ID. Corrections are
        # upserts; routine crawling adds at most the next unseen draw.
        selected_by_id = {row["id"]: row for row in selected if self._valid_result(row["result"])}
        if not selected_by_id:
            if failures:
                logger.warning("fallback sources had failures: {}", "; ".join(failures))
            logger.info("Power 6/55 already current at #{:05d}; no unseen draw found", current_max_id)
            return True

        self._store_fallback_rows(list(selected_by_id.values()))
        logger.info(
            "Power 6/55 fallback stored ids={} current_max={} sources={}",
            sorted(selected_by_id), current_max_id, list(self.FALLBACK_URLS),
        )
        return True

    def _store_fallback_rows(self, rows: List[Dict]) -> None:
        import polars as pl

        raw_path = self.product_config.raw_path
        incoming = pl.DataFrame(rows).with_columns(
            pl.col("id").cast(pl.Utf8),
            pl.col("date").cast(pl.Utf8),
        )
        if raw_path.exists():
            current = pl.read_ndjson(raw_path, infer_schema_length=None).with_columns(
                pl.col("id").cast(pl.Utf8),
                pl.col("date").cast(pl.Utf8),
            )
            incoming_ids = set(incoming["id"].to_list())
            retained = current.filter(~pl.col("id").is_in(incoming_ids))
            final = pl.concat([retained, incoming], how="diagonal_relaxed")
        else:
            final = incoming

        final = final.unique(subset=["id"], keep="last").sort(["date", "id"])
        final.write_ndjson(raw_path.absolute())
        logger.info(
            "Power 6/55 fallback upsert min_date={} max_date={} records={}",
            final["date"].min(), final["date"].max(), len(final),
        )

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
            row = {
                "date": datetime.strptime(tds[0].text.strip(), "%d/%m/%Y").strftime("%Y-%m-%d"),
                "id": tds[1].text.strip(),
                "result": [
                    int(span.text.strip())
                    for span in tds[2].find_all("span")
                    if span.text.strip() != "|"
                ],
                "process_time": datetime.now().isoformat(),
            }
            if not re.fullmatch(r"\d{5}", row["id"]):
                raise ValueError(f"Power 6/55 row has invalid draw ID: {row['id']}")
            if not self._valid_result(row["result"]):
                raise ValueError(f"Power 6/55 row {row['id']} has an invalid 6+1 result")
            data.append(row)
        return data
