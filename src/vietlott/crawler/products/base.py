import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import cattrs
import polars as pl
from loguru import logger

from vietlott.config.products import get_config
from vietlott.crawler import collections_helper
from vietlott.crawler.requests_helper import config as requests_config
from vietlott.crawler.requests_helper import fetch
from vietlott.crawler.requests_helper.fetch import get_vietlott_cookie
from vietlott.crawler.schema.requests import ORenderInfoCls


class BaseProduct:
    name = ""
    url = ""
    page_to_run: int = 1
    stored_data_dtype = {}

    org_body = None
    org_params = None

    product_config = None

    orender_info_default = ORenderInfoCls(
        SiteId="main.frontend.vi",
        SiteAlias="main.vi",
        UserSessionId="",
        SiteLang="vi",
        IsPageDesign=False,
        ExtraParam1="",
        ExtraParam2="",
        ExtraParam3="",
        SiteURL="",
        WebPage=None,
        SiteName="Vietlott",
        OrgPageAlias=None,
        PageAlias=None,
        RefKey=None,
        FullPageAlias=None,
    )

    def __init__(self):
        self.product_config = get_config(self.name)
        self.headers = requests_config.headers

        if self.product_config.use_cookies:
            self.vietlott_cookie, self.cookies = get_vietlott_cookie()
            self.headers = self.headers.copy()
            self.headers.update({"Cookie": self.vietlott_cookie})
        else:
            self.vietlott_cookie, self.cookies = None, None

    def process_result(self, params, body, res_json, task_data):
        pass

    def crawl_fallback(self, run_date_str: str, index_from: int, index_to: int) -> bool:
        """Optional fallback used when the official endpoint blocks the runner."""
        raise RuntimeError("no fallback crawler configured")

    def crawl(self, run_date_str: str, index_from: int = 0, index_to: int = 1) -> bool:
        """
        Spawn workers to get data from Vietlott.

        The crawl range is [index_from, index_to).
        """
        if index_to is None:
            index_to = self.product_config.default_index_to

        if index_to == index_from:
            index_to += 1

        if index_to <= index_from:
            index_to = index_from + 1

        page_count = index_to - index_from
        page_per_task = max(1, math.ceil(page_count / self.product_config.num_thread))
        tasks = collections_helper.chunks_iter(
            [
                {
                    "task_id": i,
                    "task_data": {
                        "params": {},
                        "body": {"PageIndex": i},
                        "run_date_str": run_date_str,
                    },
                }
                for i in range(index_from, index_to)
            ],
            page_per_task,
        )

        logger.info(
            f"there are {page_count} pages, from {index_from}..{index_to - 1}, "
            f"{page_per_task} page per task"
        )
        fetch_fn = fetch.fetch_wrapper(
            self.url,
            self.headers,
            self.org_params,
            cattrs.unstructure(self.org_body),
            self.process_result,
            self.cookies,
        )

        try:
            with ThreadPoolExecutor(max_workers=self.product_config.num_thread) as pool:
                results = list(pool.map(fetch_fn, tasks))
        except RuntimeError as exc:
            error_text = str(exc)
            if "HTTP 403" not in error_text and "HTTP 429" not in error_text:
                raise
            logger.warning(
                "official Vietlott endpoint was blocked/rate-limited; "
                f"trying validated fallback: {exc}"
            )
            return self.crawl_fallback(run_date_str, index_from, index_to)

        date_dict = defaultdict(list)
        for l1 in results:
            for l2 in l1:
                for row in l2:
                    date_dict[row["date"]].append(row)

        list_data = []
        for date, date_items in date_dict.items():
            list_data += date_items
        if len(list_data) == 0:
            logger.info("No results")
            return False

        df_crawled = pl.DataFrame(list_data).with_columns(pl.col("id").cast(pl.Utf8))
        logger.info(
            f"crawled data date: min={df_crawled['date'].min()}, max={df_crawled['date'].max()}"
            + f" id min={df_crawled['id'].min()}, max={df_crawled['id'].max()}"
            + f", records={len(df_crawled)}"
        )

        current_data_count = 0
        if self.product_config.raw_path.exists():
            current_data = pl.read_ndjson(self.product_config.raw_path, infer_schema_length=None)
            current_data = current_data.with_columns(
                pl.col("id").cast(pl.Utf8), pl.col("date").cast(pl.Utf8)
            )
            logger.info(
                f"current data date min={current_data['date'].min()}, max={current_data['date'].max()}"
                + f" id min={current_data['id'].min()}, max={current_data['id'].max()}"
                + f", records={len(current_data)}"
            )
            current_data_count = len(current_data)
            existing_ids = set(current_data["id"].to_list())
            df_take = df_crawled.filter(~pl.col("id").is_in(existing_ids))
            df_final = pl.concat([current_data, df_take])
        else:
            df_final = df_crawled

        assert isinstance(df_final, pl.DataFrame), "df_final should be a DataFrame"
        df_final = df_final.sort(["date", "id"])

        if df_final["date"].dtype != pl.Date:
            from datetime import datetime

            df_final = df_final.with_columns(
                pl.col("date").map_elements(
                    lambda x: (
                        datetime.fromisoformat(x).date()
                        if "-" in x
                        else datetime.fromtimestamp(int(x) / 1000).date()
                    ),
                    return_dtype=pl.Date,
                )
            )

        logger.info(
            f"final data min_date={df_final['date'].min()}, max_date={df_final['date'].max()}"
            + f", records={current_data_count}->{len(df_final)}, diff:{len(df_final) - current_data_count}"
        )
        df_final.write_ndjson(self.product_config.raw_path.absolute())
        logger.info(f"wrote to file {self.product_config.raw_path.absolute()}")
        return True
