"""Robust HTTP helpers for Vietlott crawling."""
from __future__ import annotations

import json
import re
import time
from typing import Callable, Optional, Tuple

import requests
from loguru import logger

from vietlott.crawler.requests_helper.config import TIMEOUT

MAX_RETRIES = 3
BACKOFF_SECONDS = 1.0


def get_vietlott_cookie() -> Tuple[str, dict]:
    res = requests.get("https://vietlott.vn/ajaxpro/", timeout=TIMEOUT)
    match = re.search(r'document.cookie="(.*?)"', res.text)
    if match is None:
        raise ValueError(f"cookie is None, text={res.text[:200]}")
    cookie = match.group(1)
    parts = cookie.split("=", 1)
    if len(parts) != 2:
        raise ValueError("invalid Vietlott cookie response")
    return cookie, {parts[0]: parts[1]}


def fetch_wrapper(
    url: str,
    headers: Optional[dict],
    org_params: Optional[dict],
    org_body: dict,
    process_result_fn: Callable,
    cookies: Optional[dict],
):
    """Return a function that fetches a chunk of tasks with retry/backoff."""
    def fetch(tasks):
        tasks_str = ",".join(str(t["task_id"]) for t in tasks)
        logger.debug(f"worker start, tasks_ids={tasks_str}")
        _headers = headers.copy() if headers is not None else {}
        results = []
        for task in tasks:
            task_id, task_data = task["task_id"], task["task_data"]
            params = org_params.copy() if org_params is not None else {}
            body = org_body.copy()
            params.update(task_data["params"])
            body.update(task_data["body"])
            last_error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    res = requests.post(url, data=json.dumps(body), params=params, headers=_headers, cookies=cookies, timeout=TIMEOUT)
                    if res.ok:
                        break
                    if res.status_code not in {408, 425, 429} and res.status_code < 500:
                        raise RuntimeError(f"HTTP {res.status_code} for task {task_id}: {res.text[:200]}")
                    last_error = RuntimeError(f"HTTP {res.status_code} for task {task_id}: {res.text[:200]}")
                except requests.RequestException as exc:
                    last_error = exc
                if attempt < MAX_RETRIES:
                    delay = BACKOFF_SECONDS * (2 ** attempt)
                    logger.warning(f"request failed for task {task_id}, retry {attempt + 1}/{MAX_RETRIES} in {delay:.1f}s")
                    time.sleep(delay)
            else:
                raise RuntimeError(f"request failed after retries for task {task_id}: {last_error}")
            if not res.ok:
                raise RuntimeError(f"request failed after retries for task {task_id}: HTTP {res.status_code}")
            try:
                result = process_result_fn(params, body, res.json(), task_data)
                results.append(result)
                logger.debug(f"task {task_id} done")
            except json.JSONDecodeError as exc:
                logger.error(f"json decode error, args={task_data}, text={res.text[:200]}")
                raise exc
        logger.debug(f"worker done, tasks={tasks_str}")
        return results
    return fetch
