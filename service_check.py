import socket
import sys
import time


def check_dns(host):
    """
    Проверяет разрешение доменного имени
    и измеряет время выполнения DNS-запроса.

    Возвращает:
        ip_address - полученный IP-адрес или None
        elapsed    - время DNS-разрешения в мс или None
    """

    start_time = time.perf_counter()

    try:
        ip_address = socket.gethostbyname(host)

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        return ip_address, elapsed

    except socket.gaierror:
        return None, None


def check_tcp(host, port, timeout=3):
    """
    Проверяет возможность установить TCP-соединение
    с заданным портом.

    Возвращает:
        success - True/False
        elapsed - время установления соединения в мс
                   или None при ошибке
    """

    start_time = time.perf_counter()

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((host, port))

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        if result == 0:
            return True, elapsed

        return False, elapsed

    except socket.error:
        return False, None

    finally:
        sock.close()


def print_dns_result(host, ip_address, elapsed):
    """Выводит результат DNS-проверки."""

    print()
    print("-" * 55)
    print("DNS-ПРОВЕРКА")
    print("-" * 55)

    print(f"Имя узла: {host}")

    if ip_address is not None:
        print(f"IP-адрес: {ip_address}")
        print(f"Время DNS-разрешения: {elapsed:.2f} мс")
    else:
        print("DNS-разрешение: ошибка")


def print_tcp_result(host, port, success, elapsed):
    """Выводит результат TCP-проверки."""

    print()
    print("-" * 55)
    print("TCP-ПРОВЕРКА")
    print("-" * 55)

    print(f"Узел: {host}")
    print(f"Порт: {port}")

    if success:
        print("TCP-соединение: установлено")

        if elapsed is not None:
            print(
                f"Время установления: "
                f"{elapsed:.2f} мс"
            )
    else:
        print("TCP-соединение: не установлено")

        if elapsed is not None:
            print(
                f"Время до получения отказа: "
                f"{elapsed:.2f} мс"
            )


def diagnostic_conclusion(
    dns_success,
    tcp_success
):
    """
    Формирует простое диагностическое заключение
    на основе результатов DNS и TCP-проверок.
    """

    print()
    print("=" * 55)
    print("ДИАГНОСТИЧЕСКОЕ ЗАКЛЮЧЕНИЕ")
    print("=" * 55)

    if not dns_success:
        print(
            "DNS: проблема с разрешением имени."
        )
        print(
            "Дальнейшая проверка сервиса по имени "
            "невозможна."
        )
        return

    print("DNS: разрешение имени успешно.")

    if tcp_success:
        print(
            "TCP: соединение с заданным портом "
            "успешно установлено."
        )
        print(
            "Диагностируемый сервис доступен "
            "на указанном порту."
        )
    else:
        print(
            "TCP: соединение с заданным портом "
            "не установлено."
        )
        print(
            "Необходимо проверить доступность сервиса, "
            "порт и правила фильтрации."
        )


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print(
            "    python service_check.py "
            "<домен_или_IP> <порт>"
        )
        print()
        print("Примеры:")
        print(
            "    python service_check.py "
            "example.com 443"
        )
        print(
            "    python service_check.py "
            "192.168.1.1 80"
        )
        sys.exit(1)

    host = sys.argv[1]

    try:
        port = int(sys.argv[2])

        if not 1 <= port <= 65535:
            raise ValueError

    except ValueError:
        print(
            "Ошибка: порт должен быть целым числом "
            "от 1 до 65535."
        )
        sys.exit(1)

    print("=" * 55)
    print("ДИАГНОСТИКА DNS И TCP")
    print("=" * 55)
    print(f"Узел: {host}")
    print(f"Порт: {port}")

    # --------------------------------------------------
    # 1. DNS
    # --------------------------------------------------

    ip_address, dns_time = check_dns(host)

    print_dns_result(
        host,
        ip_address,
        dns_time
    )

    dns_success = ip_address is not None

    # --------------------------------------------------
    # 2. TCP
    # --------------------------------------------------

    # Для TCP можно использовать как доменное имя,
    # так и непосредственно IP-адрес.
    tcp_host = ip_address if ip_address else host

    tcp_success, tcp_time = check_tcp(
        tcp_host,
        port
    )

    print_tcp_result(
        tcp_host,
        port,
        tcp_success,
        tcp_time
    )

    # --------------------------------------------------
    # 3. Итоговое заключение
    # --------------------------------------------------

    diagnostic_conclusion(
        dns_success,
        tcp_success
    )


if __name__ == "__main__":
    main()