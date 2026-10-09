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


def test_fallback_parser_resolves_yearless_xskt_archive_date():
    text = (
        "Xổ số Vietlott Power ngày 04/06 (Thứ 5) "
        "Kỳ mở thưởng: #01354 Kết quả | 23 24 28 29 39 43 "
        "Số JP2 | 45 Thống kê trúng giải"
    )
    rows = ProductPower655()._parse_fallback_text(text, source="xskt.com.vn")
    assert len(rows) == 1
    assert rows[0]["id"] == "01354"
    assert rows[0]["date"].endswith("-06-04")
    assert rows[0]["result"] == [23, 24, 28, 29, 39, 43, 45]


def test_fallback_parser_supports_baomoi_compact_draw_marker_and_date_below_result():
    text = (
        "Kết quả quay số mở thưởng Power 6/55 Giá trị Jackpot 1 "
        "Kỳ #01408 01 07 12 27 31 52 06 Thống kê giải thưởng "
        "Kỳ mở thưởng gần đây Thứ 5, 08-10-2026 Thứ 3, 06-10-2026 "
        "Thứ 7, 03-10-2026"
    )
    rows = ProductPower655()._parse_fallback_text(
        text,
        source="baomoi.com",
        reference_date="2026-10-09",
    )
    assert len(rows) == 1
    assert rows[0]["id"] == "01408"
    assert rows[0]["date"] == "2026-10-08"
    assert rows[0]["result"] == [1, 7, 12, 27, 31, 52, 6]
    assert rows[0]["source"] == "baomoi.com"


def test_official_detail_parser_does_not_drop_first_result_row():
    product = ProductPower655()
    parsed = product.process_result(
        {},
        {},
        {
            "value": {
                "HtmlContent": """
                <table>
                  <tr><th>Ngày quay</th><th>Kỳ quay</th><th>Kết quả</th></tr>
                  <tr><td>08/10/2026</td><td>01408</td>
                    <td><span>01</span> <span>07</span> <span>12</span>
                        <span>27</span> <span>31</span> <span>52</span>
                        <span>|</span> <span>06</span></td></tr>
                </table>
                """
            }
        },
        {},
    )
    assert len(parsed) == 1
    assert parsed[0]["id"] == "01408"
    assert parsed[0]["date"] == "2026-10-08"
    assert parsed[0]["result"] == [1, 7, 12, 27, 31, 52, 6]


def test_conflicting_independent_sources_are_quarantined():
    product = ProductPower655()
    row = {
        "date": "2026-10-08",
        "id": "01408",
        "result": [1, 7, 12, 27, 31, 52, 6],
        "process_time": "now",
        "source": "baomoi.com",
    }
    disagreement = {
        **row,
        "result": [2, 8, 13, 28, 32, 53, 7],
        "source": "xoso.com.vn",
    }
    assert product._resolve_source_rows({
        "01408": {"baomoi.com": row, "xoso.com.vn": disagreement}
    }) == {}


def test_official_source_disagreement_is_never_written_over_third_party_data():
    product = ProductPower655()
    third_party = {
        "date": "2026-10-08",
        "id": "01408",
        "result": [1, 7, 12, 27, 31, 52, 6],
        "process_time": "now",
        "source": "baomoi.com",
    }
    official = {
        **third_party,
        "result": [2, 8, 13, 28, 32, 53, 7],
        "source": "vietlott.vn",
    }
    assert product._resolve_source_rows({
        "01408": {"baomoi.com": third_party, "vietlott.vn": official}
    }) == {}


def test_primary_cloudflare_failure_invokes_fallback(monkeypatch, tmp_path):
    product = ProductPower655()
    product.product_config.raw_path = tmp_path / "power655.jsonl"
    called = []
    monkeypatch.setattr(
        "vietlott.crawler.products.base.fetch.fetch_wrapper",
        lambda *args, **kwargs: lambda tasks: (_ for _ in ()).throw(
            RuntimeError("HTTP 403 for task 0: Cloudflare Access denied")
        ),
    )
    monkeypatch.setattr(
        product,
        "crawl_fallback",
        lambda run_date_str, index_from, index_to: called.append(
            (run_date_str, index_from, index_to)
        ) or True,
    )
    assert product.crawl("2026-10-09", 0, 1) is True
    assert called == [("2026-10-09", 0, 1)]
