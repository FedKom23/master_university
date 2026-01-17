import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import tempfile
import os
from runpy import run_module

from async_urls import fetch_url, fetch_worker, run


class TestFetcherAsync(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_url_uses_session_get_and_returns_status(self):
        '''тестирует что fetch_url использует session.get и возвращает
        статус'''
        mock_resp = MagicMock()
        mock_resp.status = 200

        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_resp
        mock_get_cm.__aexit__.return_value = None

        session = MagicMock()
        session.get.return_value = mock_get_cm

        result = await fetch_url("http://example", session)

        session.get.assert_called_with("http://example")
        self.assertEqual(result, 200)

    async def test_fetch_worker_counts_and_handles_exceptions(self):
        '''проверяет подсчет запросов и обработку исключений в
        fetch_worker'''
        q = asyncio.Queue()
        await q.put("http://ok")
        await q.put("http://bad")
        await q.put(None)

        async def fake_fetch(url, _session):
            if url == "http://ok":
                return 200
            raise RuntimeError("boom")

        session = MagicMock()

        with patch("builtins.print") as mock_print:
            with patch(
                "async_urls.fetch_url", new=AsyncMock(side_effect=fake_fetch)
            ):
                await fetch_worker(q, session, "worker_X")

                mock_print.assert_any_call("Invalid url:", "http://bad")

                calls = mock_print.call_args_list
                fin_calls = [
                    c for c in calls
                    if c[0] and c[0][0] == "fetch_worker finished"
                ]
                self.assertTrue(
                    fin_calls,
                    "No 'fetch_worker finished' found"
                )

                last_fin = fin_calls[-1][0]
                self.assertEqual(last_fin[1], "worker_X")
                self.assertEqual(last_fin[2], 2)

    async def test_run_creates_expected_number_of_workers_and_passes_names(
        self
    ):
        '''проверяет создание нужного количества воркеров с правильными
        именами'''
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_name = tmp.name

        try:
            async def fake_worker(_q, _session, name):
                await asyncio.sleep(0)
                return name

            with patch(
                "async_urls.fetch_worker",
                new=AsyncMock(side_effect=fake_worker)
            ) as mworker:
                await run(tmp_name, 3)

                self.assertEqual(mworker.call_count, 3)
                called_names = [
                    call.args[2] for call in mworker.call_args_list
                ]
                self.assertCountEqual(
                    called_names, [f"fetcher_{i}" for i in range(3)]
                )
        finally:
            os.unlink(tmp_name)

    async def test_fetch_worker_queue_interactions(self):
        '''тестирует взаимодействие fetch_worker с очередью'''

        mock_queue = AsyncMock(spec=asyncio.Queue)

        mock_queue.get.side_effect = [
            "http://example.com",
            "http://test.org",
            None
        ]

        mock_session = MagicMock()

        with patch(
            "async_urls.fetch_url", new=AsyncMock(side_effect=[200, 404])
        ):
            with patch("builtins.print") as mock_print:
                await fetch_worker(mock_queue, mock_session, "test_worker")

                self.assertEqual(mock_queue.get.call_count, 3)

                mock_print.assert_any_call(
                    "fetch_worker:", "test_worker", "url:",
                    "http://example.com", "status:", 200
                )
                mock_print.assert_any_call(
                    "fetch_worker:", "test_worker", "url:",
                    "http://test.org", "status:", 404
                )

                mock_print.assert_any_call(
                    "fetch_worker finished", "test_worker", 2
                )


class TestMainBlock(unittest.TestCase):
    def test_main_success_calls_asyncio_run(self):
        '''проверяет успешный вызов asyncio.run в main блоке'''
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("http://example.com\n")
            tmp.flush()
            tmp_name = tmp.name

        try:
            argv = ["p", "2", tmp_name]
            with patch("sys.argv", argv):
                with patch("asyncio.run") as mock_run:
                    run_module("async_urls", run_name="__main__")
                    mock_run.assert_called_once()
        finally:
            os.unlink(tmp_name)

    def test_main_invalid_workers_raises_valueerror(self):
        '''проверяет ValueError при неверном количестве воркеров'''

        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("http://example.com\n")
            tmp.flush()
            tmp_name = tmp.name

        try:
            argv = ["p", "not_an_int", tmp_name]
            with patch("sys.argv", argv):
                with self.assertRaises(ValueError) as cm:
                    run_module("async_urls", run_name="__main__")
                self.assertIn(
                    "Invalid number of workers", str(cm.exception)
                )
        finally:
            os.unlink(tmp_name)

    def test_run_missing_file_raises_filenotfounderror(self):
        '''проверяет FileNotFoundError при отсутствующем файле'''
        with self.assertRaises(FileNotFoundError):
            asyncio.run(run("nonexistent_file.txt", 1))


class TestAsyncUrlsFullChain(unittest.IsolatedAsyncioTestCase):

    @staticmethod
    def make_response_cm(status: int):
        '''создает мок контекстного менеджера ответа с заданным статусом'''
        resp = MagicMock()
        resp.status = status

        cm = AsyncMock()
        cm.__aenter__.return_value = resp
        cm.__aexit__.return_value = None
        return cm

    def make_session_cm(self, status_by_url):
        '''создает мок сессии с предопределенными статусами для URL'''
        session = MagicMock()

        def get_side_effect(url, *_args, **_kwargs):
            if url not in status_by_url:
                raise AssertionError(
                    f"Unexpected URL requested: {url}"
                )
            return self.make_response_cm(status_by_url[url])

        session.get.side_effect = get_side_effect

        session_cm = AsyncMock()
        session_cm.__aenter__.return_value = session
        session_cm.__aexit__.return_value = None

        return session_cm, session

    async def test_fetch_url_calls_get_and_returns_status(self):
        '''проверяет вызов get и возврат статуса в fetch_url'''
        session = MagicMock()
        session.get.return_value = self.make_response_cm(204)

        status = await fetch_url("http://example", session)

        session.get.assert_called_once_with("http://example")
        self.assertEqual(status, 204)

    async def test_run_sends_requests_and_receives_statuses_for_various_sizes(
        self
    ):
        '''проверяет полную цепочку с разным количеством URL и воркеров'''
        scenarios = [
            (1, 1),
            (2, 1),
            (5, 2),
            (10, 3),
        ]

        for n_urls, workers in scenarios:
            with self.subTest(n_urls=n_urls, workers=workers):
                urls = [f"http://example/{i}" for i in range(n_urls)]
                status_by_url = {
                    u: 200 + (i % 10) for i, u in enumerate(urls)
                }

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, encoding="utf-8"
                ) as tmp:
                    tmp.write("\n".join(urls) + "\n")
                    tmp_name = tmp.name

                try:
                    session_cm, session = self.make_session_cm(status_by_url)

                    with patch(
                        "async_urls.aiohttp.ClientSession",
                        return_value=session_cm
                    ):
                        with patch("builtins.print") as mock_print:
                            await asyncio.wait_for(
                                run(tmp_name, workers), timeout=2.0
                            )

                    called_urls = [
                        c.args[0] for c in session.get.call_args_list
                    ]
                    self.assertEqual(len(called_urls), n_urls)
                    self.assertCountEqual(called_urls, urls)
                    got_status_by_url = {}
                    for c in mock_print.call_args_list:
                        args = c.args
                        if (
                            len(args) >= 6 and args[0] == "fetch_worker:" and
                            args[2] == "url:" and args[4] == "status:"
                        ):
                            got_status_by_url[args[3]] = args[5]

                    self.assertEqual(set(got_status_by_url.keys()), set(urls))
                    for u in urls:
                        self.assertEqual(got_status_by_url[u], status_by_url[u])

                    fin = [
                        c.args for c in mock_print.call_args_list
                        if c.args and c.args[0] == "fetch_worker finished"
                    ]
                    self.assertEqual(len(fin), workers)

                    names = [args[1] for args in fin]
                    self.assertCountEqual(
                        names, [f"fetcher_{i}" for i in range(workers)]
                    )

                    total_cnt = sum(args[2] for args in fin)
                    self.assertEqual(total_cnt, n_urls)

                finally:
                    os.unlink(tmp_name)


if __name__ == "__main__":
    unittest.main()
