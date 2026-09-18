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
