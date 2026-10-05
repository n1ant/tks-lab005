import socket
import subprocess
import sys
import time


def ping_host(host, count=4, timeout=2):
    """Проверяет доступность узла по ICMP."""

    successful = 0
    failed = 0
    times = []

    if sys.platform.startswith("win"):
        command = [
            "ping",
            "-n", "1",
            "-w", str(timeout * 1000),
            host
        ]
    else:
        command = [
            "ping",
            "-c", "1",
            "-W", str(timeout),
            host
        ]

    for _ in range(count):
        start = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            elapsed = (time.perf_counter() - start) * 1000

            if result.returncode == 0:
                successful += 1
                times.append(elapsed)
            else:
                failed += 1

        except OSError:
            failed += 1

    availability = successful / count * 100

    average_rtt = (
        sum(times) / len(times)
        if times else None
    )

    return {
        "successful": successful,
        "failed": failed,
        "availability": availability,
        "average_rtt": average_rtt
    }


def resolve_dns(host):
    """Проверяет разрешение имени и измеряет время DNS."""

    start = time.perf_counter()

    try:
        ip_address = socket.gethostbyname(host)

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "success": True,
            "ip": ip_address,
            "time_ms": elapsed
        }

    except socket.gaierror:
        return {
            "success": False,
            "ip": None,
            "time_ms": None
        }


def check_tcp(host, port, timeout=3):
    """Проверяет установление TCP-соединения."""

    start = time.perf_counter()

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((host, port))

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "success": result == 0,
            "time_ms": elapsed
        }

    except socket.error:
        return {
            "success": False,
            "time_ms": None
        }

    finally:
        sock.close()


def print_icmp_result(result):
    """Выводит результат ICMP-проверки."""

    print()
    print("-" * 60)
    print("1. ПРОВЕРКА ДОСТУПНОСТИ ICMP")
    print("-" * 60)

    print(
        f"Успешных попыток:   {result['successful']}"
    )

    print(
        f"Неуспешных попыток: {result['failed']}"
    )

    print(
        f"Доступность:        "
        f"{result['availability']:.2f}%"
    )

    if result["average_rtt"] is not None:
        print(
            f"Среднее время RTT:  "
            f"{result['average_rtt']:.2f} мс"
        )
    else:
        print("Среднее RTT:         нет ответа")


def print_dns_result(result):
    """Выводит результат DNS-проверки."""

    print()
    print("-" * 60)
    print("2. ПРОВЕРКА DNS")
    print("-" * 60)

    if result["success"]:
        print("DNS-разрешение: успешно")
        print(f"IP-адрес:        {result['ip']}")
        print(
            f"Время DNS:       "
            f"{result['time_ms']:.2f} мс"
        )
    else:
        print("DNS-разрешение: ошибка")


def print_tcp_result(result, port):
    """Выводит результат TCP-проверки."""

    print()
    print("-" * 60)
    print("3. ПРОВЕРКА TCP")
    print("-" * 60)

    print(f"Порт: {port}")

    if result["success"]:
        print("TCP-соединение: установлено")
        print(
            f"Время соединения: "
            f"{result['time_ms']:.2f} мс"
        )
    else:
        print("TCP-соединение: не установлено")

        if result["time_ms"] is not None:
            print(
                f"Время до отказа: "
                f"{result['time_ms']:.2f} мс"
            )


def make_conclusion(
    icmp_result,
    dns_result,
    tcp_result
):
    """
    Формирует диагностическое заключение
    по совокупности выполненных проверок.
    """

    print()
    print("=" * 60)
    print("ИТОГОВОЕ ДИАГНОСТИЧЕСКОЕ ЗАКЛЮЧЕНИЕ")
    print("=" * 60)

    if not dns_result["success"]:
        print(
            "DNS-разрешение не выполнено. "
            "Проблема может быть связана с разрешением "
            "доменного имени."
        )

        if icmp_result["successful"] > 0:
            print(
                "При этом узел отвечает на ICMP-запросы."
            )

        return

    if icmp_result["successful"] == 0:
        print(
            "ICMP-ответы отсутствуют. "
            "Это не позволяет однозначно утверждать, "
            "что узел недоступен."
        )

    else:
        print(
            "Узел отвечает на ICMP-запросы."
        )

        print(
            f"Доступность: "
            f"{icmp_result['availability']:.2f}%."
        )

    if tcp_result["success"]:
        print(
            f"TCP-порт доступен, "
            f"соединение установлено."
        )

    else:
        print(
            f"TCP-соединение с заданным портом "
            f"не установлено."
        )

    print()
    print(
        "Для локализации неисправности необходимо "
        "сопоставить результаты ICMP, маршрута, "
        "DNS и TCP-проверки."
    )


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print(
            "    python diagnostic.py "
            "<узел> <порт>"
        )
        print()
        print("Примеры:")
        print(
            "    python diagnostic.py "
            "example.com 443"
        )
        print(
            "    python diagnostic.py "
            "192.168.1.1 22"
        )
        sys.exit(1)

    host = sys.argv[1]

    try:
        port = int(sys.argv[2])

        if not 1 <= port <= 65535:
            raise ValueError

    except ValueError:
        print(
            "Ошибка: порт должен находиться "
            "в диапазоне 1–65535."
        )
        sys.exit(1)

    print("=" * 60)
    print("ПРОГРАММНАЯ ДИАГНОСТИКА TCP/IP")
    print("=" * 60)
    print(f"Узел: {host}")
    print(f"TCP-порт: {port}")

    # --------------------------------------------------
    # ICMP
    # --------------------------------------------------

    icmp_result = ping_host(host)

    print_icmp_result(icmp_result)

    # --------------------------------------------------
    # DNS
    # --------------------------------------------------

    dns_result = resolve_dns(host)

    print_dns_result(dns_result)

    # --------------------------------------------------
    # TCP
    # --------------------------------------------------

    tcp_host = (
        dns_result["ip"]
        if dns_result["success"]
        else host
    )

    tcp_result = check_tcp(
        tcp_host,
        port
    )

    print_tcp_result(
        tcp_result,
        port
    )

    # --------------------------------------------------
    # Итог
    # --------------------------------------------------

    make_conclusion(
        icmp_result,
        dns_result,
        tcp_result
    )


if __name__ == "__main__":
    main()