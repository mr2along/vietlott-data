import cattrs
import pytest

from vietlott.crawler.products.power655 import ProductPower655
from vietlott.crawler.requests_helper import config as requests_config
from vietlott.crawler.requests_helper.fetch import fetch_wrapper


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {"ok": True}
        self.text = text
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._payload


def _tasks():
    return [{"task_id": "1", "task_data": {"params": {}, "body": {"PageIndex": 1}}}]


def _wrapper():
    return fetch_wrapper(
        ProductPower655.url,
        requests_config.headers,
        ProductPower655.org_params,
        cattrs.unstructure(ProductPower655.org_body),
        lambda params, body, parsed_json, task_data: parsed_json,
        None,
    )


def test_fetch_success_is_deterministic(monkeypatch):
    calls = []

    def fake_post(*args, **kwargs):
        calls.append(kwargs["data"])
        return FakeResponse()

    monkeypatch.setattr("vietlott.crawler.requests_helper.fetch.requests.post", fake_post)
    assert _wrapper()(_tasks()) == [{"ok": True}]
    assert len(calls) == 1


def test_fetch_retries_transient_failure(monkeypatch):
    responses = iter([FakeResponse(503, text="temporary"), FakeResponse(200, {"ok": True})])

    monkeypatch.setattr(
        "vietlott.crawler.requests_helper.fetch.requests.post",
        lambda *args, **kwargs: next(responses),
    )
    monkeypatch.setattr("vietlott.crawler.requests_helper.fetch.time.sleep", lambda _: None)

    assert _wrapper()(_tasks()) == [{"ok": True}]


def test_fetch_raises_on_permanent_client_error(monkeypatch):
    monkeypatch.setattr(
        "vietlott.crawler.requests_helper.fetch.requests.post",
        lambda *args, **kwargs: FakeResponse(403, text="forbidden"),
    )

    with pytest.raises(RuntimeError, match="HTTP 403"):
        _wrapper()(_tasks())


def test_power655_fallback_parses_validated_rows(monkeypatch, tmp_path):
    html = """
    <html><body>
    <h4>KẾT QUẢ XỔ SỐ POWER 6/55 - NGÀY: 17/09/2026</h4>
    <div>Thứ năm Kỳ vé: #01399 | Ngày quay thưởng 17/09/2026
      06 11 25 27 37 45 15
    </div>
    <div>Giải thưởng</div>
    </body></html>
    """

    class Resp:
        text = html

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "vietlott.crawler.products.power655.requests.get",
        lambda *args, **kwargs: Resp(),
    )
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    assert product.crawl_fallback("2026-09-18", 0, 1) is True
    row = product.product_config.raw_path.read_text().strip()
    assert '"id":"01399"' in row
    assert '"result":[6,11,25,27,37,45,15]' in row


def test_power655_fallback_does_not_overwrite_existing_row(monkeypatch, tmp_path):
    html = """
    <html><body>
    <h4>KẾT QUẢ XỔ SỐ POWER 6/55 - NGÀY: 17/09/2026</h4>
    <div>Kỳ vé: #01399 | Ngày quay thưởng 17/09/2026
      06 11 25 27 37 45 15
    </div>
    <div>Giải thưởng</div>
    </body></html>
    """

    class Resp:
        text = html

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "vietlott.crawler.products.power655.requests.get",
        lambda *args, **kwargs: Resp(),
    )
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    product.product_config.raw_path.write_text(
        '{"date":"2026-09-17","id":"01399","result":[1,2,3,4,5,6,7],"process_time":"old"}\n',
        encoding="utf-8",
    )

    assert product.crawl_fallback("2026-09-18", 0, 1) is True
    rows = [line for line in product.product_config.raw_path.read_text().splitlines() if line.strip()]
    assert len(rows) == 1
    assert '"result":[1,2,3,4,5,6,7]' in rows[0]


def test_fallback_parser_supports_xoso_layout():
    text = (
        "Xổ số Power 6/55 Thứ Năm, 08/10/2026 "
        "Kỳ quay thưởng: #01408 01 07 12 27 31 52 06 "
        "Giải thưởng Trùng khớp"
    )
    rows = ProductPower655()._parse_fallback_text(text, source="xoso.com.vn")
    assert rows == [{
        "date": "2026-10-08",
        "id": "01408",
        "result": [1, 7, 12, 27, 31, 52, 6],
        "process_time": rows[0]["process_time"],
        "source": "xoso.com.vn",
    }]


def test_fallback_parser_supports_xskt_layout():
    text = (
        "Xổ số Power 6/55 XS Power ngày 18-7-2026 "
        "Kỳ mở thưởng: #01373 Kết quả | 22 41 45 48 54 55 "
        "Số JP2 | 16 Thống kê trúng giải"
    )
    rows = ProductPower655()._parse_fallback_text(text, source="xskt.com.vn")
    assert len(rows) == 1
    assert rows[0]["id"] == "01373"
    assert rows[0]["date"] == "2026-07-18"
    assert rows[0]["result"] == [22, 41, 45, 48, 54, 55, 16]


def test_empty_dataset_bootstraps_to_newest_draw(monkeypatch, tmp_path):
    html = """
    <html><body>
    <div>Xổ số Power 6/55 Thứ Ba, 06/10/2026 Kỳ quay thưởng: #01407
      06 07 18 20 24 27 01 Giải thưởng</div>
    <div>Xổ số Power 6/55 Thứ Năm, 08/10/2026 Kỳ quay thưởng: #01408
      01 07 12 27 31 52 06 Giải thưởng</div>
    </body></html>
    """

    class Resp:
        text = html

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "vietlott.crawler.products.power655.requests.get",
        lambda *args, **kwargs: Resp(),
    )
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    assert product.crawl_fallback("2026-10-09", 0, 1) is True
    rows = [__import__("json").loads(line) for line in product.product_config.raw_path.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["id"] == "01408"


def test_known_correction_is_refreshed_without_skipping_next_draw(monkeypatch, tmp_path):
    html = """
    <html><body>
    <div>Xổ số Power 6/55 Thứ Bảy, 05/09/2026 Kỳ quay thưởng: #01394
      03 10 20 30 40 50 06 Giải thưởng</div>
    <div>Xổ số Power 6/55 Thứ Ba, 06/10/2026 Kỳ quay thưởng: #01407
      06 07 18 20 24 27 01 Giải thưởng</div>
    <div>Xổ số Power 6/55 Thứ Năm, 08/10/2026 Kỳ quay thưởng: #01408
      01 07 12 27 31 52 06 Giải thưởng</div>
    </body></html>
    """

    class Resp:
        text = html

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "vietlott.crawler.products.power655.requests.get",
        lambda *args, **kwargs: Resp(),
    )
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    product.product_config.raw_path.write_text(
        '{"date":"2026-09-05","id":"01394","result":[1,2,3,4,5,6,7],"process_time":"old"}\\n'
        '{"date":"2026-10-06","id":"01407","result":[6,7,18,20,24,27,1],"process_time":"old"}\\n',
        encoding="utf-8",
    )
    assert product.crawl_fallback("2026-10-09", 0, 1) is True
    rows = [__import__("json").loads(line) for line in product.product_config.raw_path.read_text().splitlines()]
    by_id = {row["id"]: row for row in rows}
    assert by_id["01394"]["result"] == [3, 10, 20, 30, 40, 50, 6]
    assert by_id["01408"]["result"] == [1, 7, 12, 27, 31, 52, 6]
