import unittest
import threading
import socket
import json
from unittest.mock import patch, MagicMock, call
import sys
import os

from server import TCPServer
from client import Client


class TestTCPServerURLValidation(unittest.TestCase):
    """тесты валидации урлов"""

    def test_valid_urls(self):
        """тест проверки валидных урлов"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
            valid_urls = [
                "https://example.com",
                "https://www.google.com"
            ]

            for url in valid_urls:
                with self.subTest(url=url):
                    self.assertTrue(server.check_url(url))

    def test_invalid_urls(self):
        """тест проверки невалидных урлов"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
            invalid_urls = [
                "ftp://example.com",
                "file:///etc/passwd",
                "example.com",
                "www.google.com",
                ""
            ]

            for url in invalid_urls:
                with self.subTest(url=url):
                    self.assertFalse(server.check_url(url))

    def test_get_top_k_words_normal_case(self):
        """тест получения топ к слов в нормальном случае"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        text = "apple banana apple cherry banana apple date cherry banana"
        expected = {"apple": 3, "banana": 3, "cherry": 2}
        result = server.get_top_k_words(text, 3)
        self.assertEqual(result, expected)

    def test_get_top_k_words_empty_text(self):
        """тест с пустым текстом"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        result = server.get_top_k_words("", 3)
        self.assertEqual(result, {})

    def test_get_top_k_words_less_words_than_k(self):
        """тест когда слов меньше чем к"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        text = "apple banana"
        expected = {"apple": 1, "banana": 1}
        result = server.get_top_k_words(text, 5)
        self.assertEqual(result, expected)

    def test_get_top_k_words_different_k_values(self):
        """тест  с разными  к"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        text = "apple banana apple cherry banana apple date cherry banana"

        result_k2 = server.get_top_k_words(text, 2)
        expected_k2 = {"apple": 3, "banana": 3}
        self.assertEqual(result_k2, expected_k2)
        result_k5 = server.get_top_k_words(text, 5)
        expected_k5 = {"apple": 3, "banana": 3, "cherry": 2, "date": 1}
        self.assertEqual(result_k5, expected_k5)

    def test_worker_process_url_successfully(self):
        """тест успешной обработки урла воркером"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        mock_conn = MagicMock()

        with patch('server.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'word1 word2 word1 word3'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            server.worker_process_url(mock_conn, "http://example.com")

            mock_conn.sendall.assert_called_once()
            call_args = mock_conn.sendall.call_args[0][0]
            response_data = json.loads(call_args)

            expected = {"word1": 2, "word2": 1, "word3": 1}
            self.assertEqual(response_data, expected)
            self.assertEqual(server.processed, 1)

    def test_worker_handles_invalid_url(self):
        """тест обработки невалидного урла воркером"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        mock_conn = MagicMock()

        server.worker_process_url(mock_conn, "ftp://example.com")

        mock_conn.sendall.assert_called_once()
        call_args = mock_conn.sendall.call_args[0][0]
        response_data = json.loads(call_args)

        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "Invalid URL")

    def test_worker_handles_http_error(self):
        """тест обработки http ошибки"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        mock_conn = MagicMock()

        with patch('server.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = OSError("Connection failed")

            server.worker_process_url(mock_conn, "http://example.com")

            mock_conn.sendall.assert_called_once()
            call_args = mock_conn.sendall.call_args[0][0]
            response_data = json.loads(call_args)

            self.assertIn("error", response_data)
            self.assertEqual(response_data["error"], "Connection failed")

    def test_worker_connection_closed_after_processing(self):
        """тест что соединение закрывается после обработки"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        mock_conn = MagicMock()

        with patch('server.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'test data'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            server.worker_process_url(mock_conn, "http://example.com")
            mock_conn.close.assert_called_once()


class TestTCPServerLifecycle(unittest.TestCase):
    """тесты жизненного цикла сервера"""

    def setUp(self):
        self.original_argv = sys.argv

    def test_server_initialization_with_wrong_argument_count(self):
        """тест инициализации сервера с неправильным количеством аргументов"""
        sys.argv = ['server.py', '-w', '2']

        with self.assertRaises(SystemExit) as cm:
            _ = TCPServer("127.0.0.1", 6001)

        sys.argv = self.original_argv
        self.assertEqual(cm.exception.code, 1)

    def test_run_starts_workers(self):
        """тест что run запускает worker потоки"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        with patch.object(server, 'start_workers') as mock_start_workers, \
                patch('socket.socket') as mock_socket_class:

            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket
            mock_socket.accept.side_effect = socket.error("Test exit")

            server.run()

            mock_socket.bind.assert_called_with(("127.0.0.1", 6001))
            mock_socket.listen.assert_called_with(5)
            mock_start_workers.assert_called_once()

    def test_run_accepts_connections(self):
        """тест что run принимает соединения и добавляет в очередь"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        with patch('socket.socket') as mock_socket_class, \
                patch.object(server, 'start_workers'), \
                patch.object(server.queue, 'put') as mock_queue_put:

            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket

            mock_conn = MagicMock()
            mock_addr = ('127.0.0.1', 12345)

            mock_socket.accept.side_effect = [
                (mock_conn, mock_addr),
                (mock_conn, mock_addr),
                socket.error("Test exit")
            ]
            mock_conn.recv.side_effect = [
                b'http://example.com',
                b''
            ]

            server.run()
            mock_socket.accept.assert_called()
            self.assertEqual(mock_conn.recv.call_count, 2)
            self.assertEqual(mock_queue_put.call_count, 3)
            args = mock_queue_put.call_args_list[0][0][0]
            self.assertEqual(args[0], mock_conn)
            self.assertEqual(args[1], b'http://example.com')

    def test_run_handles_socket_errors(self):
        """тест что run обрабатывает ошибки сокета"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value = mock_socket
            mock_socket.accept.side_effect = socket.error("Connection error")

            server.run()

            self.assertTrue(mock_socket.close.called)

    def test_server_thread_creation(self):
        """тест создания потоков сервера"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6004)
            server.start_workers()

            self.assertEqual(len(server.worker_threads), 2)

            for i, thread in enumerate(server.worker_threads):
                self.assertEqual(thread.name, f"Worker-{i}")
                self.assertTrue(thread.daemon)

    def test_start_workers_creates_correct_number_of_threads(self):
        """тест что start_workers создает правильное количество потоков"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
            server.start_workers()

            self.assertEqual(len(server.worker_threads), 2)

            for i, thread in enumerate(server.worker_threads):
                self.assertEqual(thread.name, f"Worker-{i}")
                self.assertTrue(thread.daemon)
                self.assertTrue(thread.is_alive())

    def test_worker_thread_lifecycle(self):
        """тест жизни worker потока"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
            server.queue.put(None)

            worker_thread = threading.Thread(target=server.worker)
            worker_thread.daemon = True
            worker_thread.start()
            worker_thread.join(timeout=1.0)

            self.assertFalse(worker_thread.is_alive())

    def test_worker_processes_multiple_tasks(self):
        """тест что воркер обрабатывает несколько задач из очереди"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6001)
            mock_conn1 = MagicMock()
            mock_conn2 = MagicMock()

            server.queue.put((mock_conn1, b"http://example1.com"))
            server.queue.put((mock_conn2, b"http://example2.com"))
            server.queue.put(None)

            with patch('server.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'test data'
                mock_response.__enter__.return_value = mock_response
                mock_urlopen.return_value = mock_response

                server.worker()

                self.assertEqual(mock_conn1.sendall.call_count, 1)
                self.assertEqual(mock_conn2.sendall.call_count, 1)
                self.assertEqual(server.processed, 2)


class TestClientArgumentParsing(unittest.TestCase):
    """тесты парсинга аргументов клиента"""

    def test_get_info_valid(self):
        """тест получения корректных аргументов"""
        with patch('sys.argv', ['client.py', '3', 'test_urls.txt']):
            client = Client("127.0.0.1", 6001)

            num_threads, filename = client.get_info()
            self.assertEqual(num_threads, 3)
            self.assertEqual(filename, 'test_urls.txt')

    def test_get_info_invalid_args(self):
        """тест обработки неправильных аргументов"""
        with patch('sys.argv', ['client.py']):
            with self.assertRaises(SystemExit) as cm:
                _ = Client("127.0.0.1", 6001)
            self.assertEqual(cm.exception.code, 1)


class TestClientThreadManagement(unittest.TestCase):
    """тесты управления потоками клиента"""

    def test_client_thread_creation(self):
        """тест создания потоков клиента"""
        with patch('sys.argv', ['client.py', '4', 'test.txt']):
            client = Client("127.0.0.1", 6004)
            client.num_threads = 4
            client.start_workers()

            self.assertEqual(len(client.worker_threads), 4)

            for i, thread in enumerate(client.worker_threads):
                self.assertEqual(thread.name, f"Client-{i}")
                self.assertTrue(thread.daemon)


class TestIntegration(unittest.TestCase):
    """итеграционные тесты клиент-серверного взаимодействия"""

    def test_client_server_communication(self):
        """тест базового взаимодействия клиент-сервер"""
        with open('test_urls.txt', 'w', encoding='utf-8') as f:
            f.write("http://example.com\n")
            f.write("invalid_url\n")

        try:
            with patch('sys.argv', ['client.py', '2', 'test_urls.txt']):
                client = Client("127.0.0.1", 6002)

            with patch('socket.socket') as mock_socket:
                mock_conn = MagicMock()
                mock_socket.return_value.__enter__.return_value = mock_conn
                response = json.dumps({"test": 1}).encode('utf-8')
                mock_conn.recv.return_value = response

                with patch('builtins.print'):
                    client.run()

                self.assertTrue(mock_socket.called)
                self.assertEqual(mock_conn.sendall.call_count, 2)

        finally:
            if os.path.exists('test_urls.txt'):
                os.remove('test_urls.txt')

    def test_server_client_integration_flow(self):
        """тест полного потока обработки URL сервером и клиентом"""
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            server = TCPServer("127.0.0.1", 6002)

        with open('test_urls.txt', 'w', encoding='utf-8') as f:
            f.write("http://example.com\n")

        try:
            with patch('server.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'test example data'
                mock_response.__enter__.return_value = mock_response
                mock_urlopen.return_value = mock_response

                mock_conn = MagicMock()
                server.worker_process_url(mock_conn, "http://example.com")

                mock_conn.sendall.assert_called_once()
                call_args = mock_conn.sendall.call_args[0][0]
                response_data = json.loads(call_args)

                expected_words = {"test": 1, "example": 1, "data": 1}
                self.assertEqual(response_data, expected_words)
                self.assertEqual(server.processed, 1)

        finally:
            if os.path.exists('test_urls.txt'):
                os.remove('test_urls.txt')


class TestTCPServerStatistics(unittest.TestCase):
    """тесты статистики сервера"""

    def setUp(self):
        with patch('sys.argv', ['server.py', '-w', '2', '-k', '3']):
            self.server = TCPServer("127.0.0.1", 6001)

    def test_worker_statistics_output(self):
        """Тест вывода статистики воркером"""

        mock_conn = MagicMock()

        with patch('server.urlopen') as mock_urlopen, \
             patch('builtins.print') as mock_print:

            mock_response = MagicMock()
            mock_response.read.return_value = b'test data'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            self.server.worker_process_url(mock_conn, "http://example1.com")
            self.server.worker_process_url(mock_conn, "http://example2.com")

            expected_calls = [
                call("[INFO] Processed 1 URLs"),
                call("[INFO] Processed 2 URLs")
            ]
            mock_print.assert_has_calls(expected_calls, any_order=False)


def create_test_urls_file():
    """Создание тестового файла с URL для интеграционных тестов"""
    urls = [
        "http://example.com",
        "https://www.google.com",
        "http://invalid.url.that.should.fail"
    ]

    with open('test_urls_integration.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')


if __name__ == '__main__':
    create_test_urls_file()

    unittest.main(verbosity=2)

    if os.path.exists('test_urls_integration.txt'):
        os.remove('test_urls_integration.txt')
