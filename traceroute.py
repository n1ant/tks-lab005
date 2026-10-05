import socket
import struct
import sys
import time


def traceroute(host, max_hops=30, timeout=2):
    """
    Определяет маршрут до заданного узла путем
    последовательного увеличения значения TTL.

    Для каждого перехода выводится:
        - номер перехода;
        - IP-адрес узла;
        - время ответа.

    Возвращает список результатов трассировки.
    """

    try:
        destination = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Ошибка: не удалось разрешить имя узла {host}")
        return []

    print("=" * 65)
    print("ТРАССИРОВКА МАРШРУТА")
    print("=" * 65)
    print(f"Узел: {host}")
    print(f"IP:   {destination}")
    print()

    results = []

    for ttl in range(1, max_hops + 1):
        # Сокет для получения ICMP-сообщений
        recv_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_RAW,
            socket.IPPROTO_ICMP
        )

        # Сокет для отправки UDP-пакета
        send_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )

        recv_socket.settimeout(timeout)

        # Устанавливаем TTL для текущего перехода
        send_socket.setsockopt(
            socket.SOL_IP,
            socket.IP_TTL,
            ttl
        )

        try:
            recv_socket.bind(("", 33434))

            start_time = time.perf_counter()

            # Отправляем UDP-пакет на заведомо закрытый
            # или неназначенный порт.
            send_socket.sendto(
                b"traceroute",
                (destination, 33434)
            )

            try:
                _, address = recv_socket.recvfrom(512)

                elapsed = (
                    time.perf_counter() - start_time
                ) * 1000

                router_ip = address[0]

                results.append({
                    "hop": ttl,
                    "address": router_ip,
                    "time_ms": elapsed
                })

                print(
                    f"{ttl:2d}  "
                    f"{router_ip:<15}  "
                    f"{elapsed:8.2f} мс"
                )

                # Если ответ пришел от конечного узла,
                # трассировка завершена.
                if router_ip == destination:
                    break

            except socket.timeout:
                results.append({
                    "hop": ttl,
                    "address": "*",
                    "time_ms": None
                })

                print(
                    f"{ttl:2d}  "
                    f"{'*':<15}  "
                    f"нет ответа"
                )

        finally:
            send_socket.close()
            recv_socket.close()

    return results


def print_summary(results):
    """Выводит краткую сводку результатов."""

    print()
    print("=" * 65)
    print("СВОДКА")
    print("=" * 65)

    if not results:
        print("Результаты отсутствуют.")
        return

    print(
        f"{'Переход':<10}"
        f"{'Узел':<20}"
        f"{'Время, мс':<15}"
    )

    print("-" * 45)

    for item in results:
        if item["time_ms"] is None:
            time_text = "нет ответа"
        else:
            time_text = f"{item['time_ms']:.2f}"

        print(
            f"{item['hop']:<10}"
            f"{item['address']:<20}"
            f"{time_text:<15}"
        )


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print(
            "    python traceroute.py <адрес> "
            "[максимальное_число_переходов]"
        )
        print()
        print("Пример:")
        print("    python traceroute.py 8.8.8.8")
        print("    python traceroute.py example.com 20")
        sys.exit(1)

    host = sys.argv[1]

    if len(sys.argv) >= 3:
        try:
            max_hops = int(sys.argv[2])

            if max_hops <= 0:
                raise ValueError

        except ValueError:
            print(
                "Ошибка: максимальное число переходов "
                "должно быть положительным целым."
            )
            sys.exit(1)
    else:
        max_hops = 30

    results = traceroute(
        host,
        max_hops=max_hops
    )

    print_summary(results)


if __name__ == "__main__":
    main()