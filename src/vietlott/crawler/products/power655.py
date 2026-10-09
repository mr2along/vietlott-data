from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
import re
import requests
from loguru import logger
from urllib.parse import urlparse

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

    # Primary crawling uses Vietlott's Ajax endpoint. These sources are only used
    # when that endpoint is blocked, rate-limited, unavailable, or returns a challenge.
    FALLBACK_URL = "https://baomoi.com/tien-ich-ket-qua-vietlott-power655.epi"
    FALLBACK_URLS = (
        FALLBACK_URL,
        "https://xoso.com.vn/xo-so-power-655.html",
        "https://xskt.com.vn/xspower/200-ngay",
    )
    OFFICIAL_DETAIL_URL = (
        "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655"
        "?id={draw_id}&nocatche=1"
    )
    KNOWN_CORRECTION_ID = "01394"
    REQUEST_TIMEOUT_SECONDS = 20
    USER_AGENT = (
        "Mozilla/5.0 (compatible; vietlott-data/0.4; "
        "+https://github.com/mr2along/vietlott-data)"
    )
    SOURCE_PRIORITY = {
        "vietlott.vn": 0,
        "baomoi.com": 1,
        "xoso.com.vn": 2,
        "xskt.com.vn": 3,
    }

    # Handles the official detail pages and common public-history page variants,
    # including Bao Moi's compact "Kỳ #01408" format.
    _DRAW_MARKER = re.compile(
        r"\bKỳ(?:\s+(?:quay\s+thưởng|mở\s+thưởng|vé))?\s*:?\s*#?\s*(\d{5})\b",
        re.IGNORECASE,
    )
    _DATE = re.compile(
        r"(?<!\d)(\d{1,2}[/-]\d{1,2}(?:[/-]\d{4})?)(?!\d)"
    )
    _NUMBER = re.compile(r"(?<![\w])(\d{1,2})(?![\w])")
    _BLOCK_PAGE_MARKERS = (
        "just a moment",
        "attention required",
        "checking your browser",
        "verify you are human",
        "cf-ray",
    )

    def _valid_result(self, result: List[int]) -> bool:
        return (
            len(result) == 7
            and len(set(result[:6])) == 6
            and all(1 <= n <= 55 for n in result)
            and result[6] not in result[:6]
        )

    @staticmethod
    def _reference_date(reference_date=None) -> date:
        if isinstance(reference_date, datetime):
            return reference_date.date()
        if isinstance(reference_date, date):
            return reference_date
        if reference_date:
            try:
                return datetime.strptime(str(reference_date)[:10], "%Y-%m-%d").date()
            except ValueError:
                pass
        return datetime.now().date()

    def _date_to_iso(self, text: str, reference_date=None) -> str:
        normalized = text.replace("-", "/")
        parts = normalized.split("/")
        if len(parts) == 3:
            return datetime.strptime(normalized, "%d/%m/%Y").date().isoformat()
        if len(parts) != 2:
            raise ValueError(f"unsupported date: {text}")

        day, month = int(parts[0]), int(parts[1])
        reference = self._reference_date(reference_date)
        candidates = []
        for year in (reference.year, reference.year - 1):
            try:
                candidates.append(date(year, month, day))
            except ValueError:
                continue
        plausible = [candidate for candidate in candidates if candidate <= reference + timedelta(days=1)]
        if not plausible:
            raise ValueError(f"yearless date is in the future or invalid: {text}")
        # Use the latest plausible occurrence. The archive is finite (about 200 days),
        # so this also resolves January/December year boundaries deterministically.
        return max(plausible).isoformat()

    def _parse_fallback_text(
        self,
        text: str,
        source: str = "unknown",
        reference_date=None,
    ) -> List[Dict]:
        """Parse and validate draw rows from an official detail page or public history page."""
        normalized = re.sub(r"\s+", " ", text).strip()
        markers = list(self._DRAW_MARKER.finditer(normalized))
        rows: List[Dict] = []
        source_date = self._reference_date(reference_date)

        for index, marker in enumerate(markers):
            draw_id = marker.group(1)
            start = marker.end()
            end = markers[index + 1].start() if index + 1 < len(markers) else len(normalized)
            segment = normalized[start:end]

            # Draw date may be before the ID (xoso/xskt), after it (official result
            # detail pages), or in Bao Moi's "recent draws" section after the result.
            context_start = max(0, marker.start() - 180)
            context_end = min(len(normalized), marker.end() + 1600)
            date_matches = list(self._DATE.finditer(normalized, context_start, context_end))
            valid_dates = []
            for date_match in date_matches:
                date_text = date_match.group(1)
                try:
                    parsed_date = self._date_to_iso(date_text, source_date)
                    parsed_day = date.fromisoformat(parsed_date)
                    if parsed_day > source_date + timedelta(days=1):
                        continue
                    # Reject false date-like fragments such as the product label "6/55".
                    valid_dates.append((abs(date_match.start() - marker.start()), parsed_date, date_text))
                except ValueError:
                    continue
            if not valid_dates:
                logger.warning("fallback row {} from {} has no valid date", draw_id, source)
                continue
            _, draw_date, date_text = min(valid_dates, key=lambda item: item[0])

            # Dates must not become lottery numbers. The winning numbers are the first
            # valid 6+1 sequence after the draw marker; later prize amounts/statistics
            # are deliberately ignored.
            result_text = self._DATE.sub(" ", segment)
            tokens = [int(value) for value in self._NUMBER.findall(result_text)[:30]]
            result = None
            for offset in range(max(0, len(tokens) - 6)):
                candidate = tokens[offset : offset + 7]
                if self._valid_result(candidate):
                    result = candidate
                    break
            if result is None:
                logger.warning(
                    "fallback row {} from {} has no valid 6+1 result; first tokens={}",
                    draw_id,
                    source,
                    tokens[:12],
                )
                continue

            rows.append(
                {
                    "date": draw_date,
                    "id": draw_id,
                    "result": result,
                    "process_time": datetime.now().isoformat(),
                    "source": source,
                }
            )
        # Defensive dedupe: a page can include the same result in both a card and a table.
        by_id: Dict[str, Dict] = {}
        for row in rows:
            previous = by_id.get(row["id"])
            if previous and (previous["date"], previous["result"]) != (row["date"], row["result"]):
                logger.error("source {} contains conflicting versions of draw #{}", source, row["id"])
                by_id.pop(row["id"], None)
                continue
            by_id.setdefault(row["id"], row)
        return list(by_id.values())

    def _fetch_page_text(self, url: str) -> str:
        response = requests.get(
            url,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        page_text = response.text or ""
        lowered = page_text.lower()
        if any(marker in lowered for marker in self._BLOCK_PAGE_MARKERS):
            # Some anti-bot challenges are returned with HTTP 200.
            raise RuntimeError(f"source returned a Cloudflare/anti-bot challenge: {url}")
        return page_text

    def _fetch_fallback_source(self, url: str, reference_date=None) -> List[Dict]:
        html = self._fetch_page_text(url)
        soup = BeautifulSoup(html, "lxml")
        source = urlparse(url).netloc.lower().removeprefix("www.")
        rows = self._parse_fallback_text(
            soup.get_text(" ", strip=True),
            source=source,
            reference_date=reference_date,
        )
        logger.info("Power 6/55 fallback source={} parsed_valid_rows={}", source, len(rows))
        if not rows:
            raise RuntimeError(f"Power 6/55 fallback source returned no validated draws: {url}")
        return rows

    def _fetch_official_detail(self, draw_id: str, reference_date=None) -> Optional[Dict]:
        """Fetch one draw from Vietlott's public official result-detail page."""
        url = self.OFFICIAL_DETAIL_URL.format(draw_id=draw_id)
        html = self._fetch_page_text(url)
        soup = BeautifulSoup(html, "lxml")
        rows = self._parse_fallback_text(
            soup.get_text(" ", strip=True),
            source="vietlott.vn",
            reference_date=reference_date,
        )
        for row in rows:
            if row["id"] == draw_id:
                return row
        raise RuntimeError(f"official Vietlott detail page did not contain requested draw #{draw_id}")

    @staticmethod
    def _row_signature(row: Dict):
        return row["date"], tuple(row["result"])

    def _resolve_source_rows(self, source_rows: Dict[str, Dict[str, Dict]]) -> Dict[str, Dict]:
        """Prefer official data, otherwise require agreement or use a logged degraded fallback."""
        resolved: Dict[str, Dict] = {}
        for draw_id, versions in source_rows.items():
            official = versions.get("vietlott.vn")
            other_versions = {
                source: row for source, row in versions.items() if source != "vietlott.vn"
            }
            if official:
                official_signature = self._row_signature(official)
                mismatches = [
                    source
                    for source, row in other_versions.items()
                    if self._row_signature(row) != official_signature
                ]
                if mismatches:
                    logger.error(
                        "source conflict for draw #{}: official Vietlott disagrees with {}. "
                        "Quarantining this draw instead of overwriting data.",
                        draw_id,
                        mismatches,
                    )
                    continue
                resolved[draw_id] = official
                continue

            signature_groups: Dict[tuple, List[Dict]] = {}
            for source, row in other_versions.items():
                signature_groups.setdefault(self._row_signature(row), []).append(row)
            if not signature_groups:
                continue
            ranked_groups = sorted(
                signature_groups.values(),
                key=lambda group: (
                    -len(group),
                    min(self.SOURCE_PRIORITY.get(row["source"], 99) for row in group),
                ),
            )
            best = ranked_groups[0]
            if len(ranked_groups) > 1 and len(best) == len(ranked_groups[1]):
                logger.error(
                    "source conflict for draw #{}: no source majority; quarantining row",
                    draw_id,
                )
                continue
            if len(best) == 1:
                logger.warning(
                    "DEGRADED_SOURCE: draw #{} accepted from one validated source ({}) "
                    "because official verification/independent agreement was unavailable",
                    draw_id,
                    best[0]["source"],
                )
            elif len(other_versions) > 1:
                logger.info(
                    "source consensus for draw #{} from {}",
                    draw_id,
                    [row["source"] for row in best],
                )
            # Prefer Bao Moi within an agreeing group so the provenance is stable.
            resolved[draw_id] = min(
                best,
                key=lambda row: self.SOURCE_PRIORITY.get(row["source"], 99),
            )
        return resolved

    def crawl_fallback(self, run_date_str: str, index_from: int, index_to: int) -> bool:
        """Recover Power 6/55 from official result pages and independent public sources."""
        reference_date = self._reference_date(run_date_str)
        source_rows: Dict[str, Dict[str, Dict]] = {}
        failures: List[str] = []

        # Read existing state first. It is also used to probe the likely next draw
        # directly on the official result-detail page if the Ajax endpoint is blocked.
        import polars as pl

        raw_path = self.product_config.raw_path
        current = (
            pl.read_ndjson(raw_path, infer_schema_length=None)
            if raw_path.exists()
            else pl.DataFrame()
        )
        current_ids = set()
        current_max_id = 0
        if current.height and "id" in current.columns:
            current = current.with_columns(pl.col("id").cast(pl.Utf8))
            current_ids = set(current["id"].to_list())
            if current_ids:
                current_max_id = max(int(value) for value in current_ids)

        for url in self.FALLBACK_URLS:
            try:
                for row in self._fetch_fallback_source(url, reference_date):
                    source = row["source"]
                    source_rows.setdefault(row["id"], {}).setdefault(source, row)
            except Exception as exc:
                message = f"{url}: {exc}"
                failures.append(message)
                logger.warning("Power 6/55 fallback source failed: {}", message)

        # Bao Moi and the two archives help discover draw IDs. Verify the latest
        # candidates against Vietlott's own detail page where that page is reachable.
        candidate_ids = set()
        all_candidate_ids = [int(draw_id) for draw_id in source_rows]
        candidate_ids.update(f"{draw_id:05d}" for draw_id in sorted(all_candidate_ids, reverse=True)[:3])
        if current_max_id:
            candidate_ids.add(f"{current_max_id + 1:05d}")
            candidate_ids.add(f"{current_max_id:05d}")
        for draw_id in sorted(candidate_ids, key=int, reverse=True)[:4]:
            try:
                official_row = self._fetch_official_detail(draw_id, reference_date)
                if official_row:
                    source_rows.setdefault(draw_id, {})["vietlott.vn"] = official_row
            except Exception as exc:
                message = f"official detail #{draw_id}: {exc}"
                failures.append(message)
                logger.info("Power 6/55 official detail fallback unavailable: {}", message)

        rows_by_id = self._resolve_source_rows(source_rows)
        if not rows_by_id:
            error_text = "; ".join(failures) if failures else "all sources returned no consistent draws"
            raise RuntimeError("All Power 6/55 fallback sources failed or conflicted: " + error_text)

        rows = sorted(rows_by_id.values(), key=lambda row: (int(row["id"]), row["date"]))
        selected: List[Dict] = []

        # The historically identified correction is upserted when it is actually
        # available and sources agree. It must never replace the next unseen draw.
        correction = rows_by_id.get(self.KNOWN_CORRECTION_ID)
        if correction is not None:
            selected.append(correction)

        if index_from == 0 and index_to <= 1:
            if not current.height:
                # Keep bootstrap deterministic; the next run/backfill recovers older rows.
                selected.append(max(rows, key=lambda row: int(row["id"])))
            else:
                # Repair visible gaps and persist only the earliest unseen ID. The
                # scheduled workflow repeats this operation to catch up sequentially.
                recoverable_gaps = [
                    row for row in rows
                    if int(row["id"]) < current_max_id and row["id"] not in current_ids
                ]
                selected.extend(recoverable_gaps)
                unseen = [row for row in rows if int(row["id"]) > current_max_id]
                if unseen:
                    selected.append(min(unseen, key=lambda row: int(row["id"])))
        else:
            # Fallback archives are not the official API's page layout. Map their
            # stable, descending draw-ID order to the project's six-draw page size.
            descending = sorted(rows, key=lambda row: int(row["id"]), reverse=True)
            page_size = max(1, int(getattr(self.product_config, "page_size", 6)))
            left = max(0, index_from) * page_size
            right = max(left, index_to * page_size)
            selected.extend(descending[left:right])

        selected_by_id = {
            row["id"]: row for row in selected if self._valid_result(row["result"])
        }
        if not selected_by_id:
            if failures:
                logger.warning("fallback completed with unavailable sources: {}", "; ".join(failures))
            logger.info(
                "Power 6/55 fallback found no rows for requested range; current_max=#{:05d}",
                current_max_id,
            )
            return True

        self._store_fallback_rows(list(selected_by_id.values()))
        logger.info(
            "Power 6/55 fallback stored ids={} sources={} failed_sources={}",
            sorted(selected_by_id, key=int),
            sorted({row.get("source", "unknown") for row in selected_by_id.values()}),
            len(failures),
        )
        return True

    def _store_fallback_rows(self, rows: List[Dict]) -> None:
        import polars as pl

        raw_path = self.product_config.raw_path
        raw_path.parent.mkdir(parents=True, exist_ok=True)
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
        # Write atomically so an interrupted runner cannot leave truncated NDJSON.
        temporary_path = raw_path.with_name(raw_path.name + ".tmp")
        final.write_ndjson(temporary_path)
        temporary_path.replace(raw_path)
        logger.info(
            "Power 6/55 fallback upsert min_date={} max_date={} records={}",
            final["date"].min(),
            final["date"].max(),
            len(final),
        )

    def process_result(self, params, body, res_json, task_data) -> List[Dict]:
        """Parse and validate rows returned by Vietlott's official Ajax endpoint."""
        html = res_json.get("value", {}).get("HtmlContent")
        if not html:
            raise ValueError("Power 6/55 response does not contain HtmlContent")
        soup = BeautifulSoup(html, "lxml")
        data: List[Dict] = []
        for tr in soup.select("tr"):
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            date_text = tds[0].get_text(" ", strip=True)
            draw_id = tds[1].get_text(" ", strip=True).replace("#", "").strip()
            if not re.fullmatch(r"\d{5}", draw_id):
                # Ignore table headers and unrelated layout rows.
                continue
            try:
                draw_date = datetime.strptime(date_text, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                logger.warning("Skipping official Power 6/55 row #{} with invalid date {}", draw_id, date_text)
                continue

            result_cell = tds[2]
            spans = [span.get_text(strip=True) for span in result_cell.find_all("span")]
            number_text = " ".join(spans) if spans else result_cell.get_text(" ", strip=True)
            numbers = [int(value) for value in self._NUMBER.findall(number_text)]
            row = {
                "date": draw_date,
                "id": draw_id,
                "result": numbers[:7],
                "process_time": datetime.now().isoformat(),
            }
            if not self._valid_result(row["result"]):
                logger.warning(
                    "Skipping malformed official Power 6/55 row #{} result={}",
                    draw_id,
                    row["result"],
                )
                continue
            data.append(row)

        if not data:
            raise ValueError("Power 6/55 official response contained no valid result rows")
        return data
