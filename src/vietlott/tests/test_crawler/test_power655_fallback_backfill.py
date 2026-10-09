import json
from datetime import date
from pathlib import Path

from vietlott.crawler.products.power655 import ProductPower655


def _draw(draw_id: str, draw_date: str, numbers: list[int]) -> str:
    formatted_date = date.fromisoformat(draw_date).strftime("%d/%m/%Y")
    return (
        f"<h4>KẾT QUẢ XỔ SỐ POWER 6/55 - NGÀY: {formatted_date}</h4>"
        f"<div>Kỳ vé: #{draw_id} | Ngày quay thưởng {formatted_date} "
        f"{' '.join(map(str, numbers))}</div><div>Giải thưởng</div>"
    )


def test_multi_page_fallback_backfills_all_draws(monkeypatch, tmp_path: Path) -> None:
    """A multi-page request starting at index 0 is a backfill, not a daily crawl."""
    latest_html = _draw("01408", "2026-10-08", [15, 16, 17, 18, 19, 20, 21])
    history_html = (
        _draw("01406", "2026-10-03", [1, 2, 3, 4, 5, 6, 7])
        + _draw("01407", "2026-10-06", [8, 9, 10, 11, 12, 13, 14])
    )

    class Response:
        def __init__(self, html: str) -> None:
            self.text = html

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, **kwargs: object) -> Response:
        if url == ProductPower655.FALLBACK_URL:
            return Response(latest_html)
        return Response(history_html)

    monkeypatch.setattr("vietlott.crawler.products.power655.requests.get", fake_get)
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    product.product_config.raw_path.write_text(
        '{"date":"2026-10-01","id":"01405","result":[22,23,24,25,26,27,28],"process_time":"old"}\n',
        encoding="utf-8",
    )

    assert product.crawl_fallback("2026-10-09", 0, 2) is True
    ids = [
        row["id"]
        for row in (
            json.loads(line)
            for line in product.product_config.raw_path.read_text(encoding="utf-8").splitlines()
        )
    ]
    assert ids == ["01405", "01406", "01407", "01408"]


def test_single_page_incremental_crawl_recovers_recent_gap(monkeypatch, tmp_path: Path) -> None:
    """The latest fallback page can repair an internal gap without overwriting existing draws."""
    latest_html = (
        _draw("01407", "2026-10-06", [8, 9, 10, 11, 12, 13, 14])
        + _draw("01408", "2026-10-08", [15, 16, 17, 18, 19, 20, 21])
    )

    class Response:
        text = latest_html

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "vietlott.crawler.products.power655.requests.get",
        lambda *args, **kwargs: Response(),
    )
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    product.product_config.raw_path.write_text(
        """{"date":"2026-10-03","id":"01406","result":[1,2,3,4,5,6,7],"process_time":"old"}
{"date":"2026-10-08","id":"01408","result":[22,23,24,25,26,27,28],"process_time":"keep"}
""",
        encoding="utf-8",
    )

    assert product.crawl_fallback("2026-10-09", 0, 1) is True
    rows = [
        json.loads(line)
        for line in product.product_config.raw_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [row["id"] for row in rows] == ["01406", "01407", "01408"]
    assert rows[-1]["result"] == [22, 23, 24, 25, 26, 27, 28]
