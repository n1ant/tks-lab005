import platform
import subprocess
import sys
import time


def ping_host(host, count=4, timeout=2):
    """
    Проверяет доступность узла и измеряет время ответа.

    Возвращает:
        successful - количество успешных попыток
        failed     - количество неуспешных попыток
        times      - список времен успешных ответов в мс
    """

    successful = 0
    failed = 0
    times = []

    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
    else:
        command = ["ping", "-c", "1", "-W", str(timeout), host]

    for attempt in range(1, count + 1):
        start_time = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            elapsed = (time.perf_counter() - start_time) * 1000

            if result.returncode == 0:
                successful += 1
                times.append(elapsed)

                print(
                    f"[{attempt}/{count}] "
                    f"{host}: ответ получен, "
                    f"RTT = {elapsed:.2f} мс"
                )
            else:
                failed += 1

                print(
                    f"[{attempt}/{count}] "
                    f"{host}: ответа нет"
                )

        except OSError as error:
            failed += 1

            print(
                f"[{attempt}/{count}] "
                f"{host}: ошибка запуска ping: {error}"
            )

        if attempt < count:
            time.sleep(0.5)

    availability = successful / count * 100

    return successful, failed, times, availability


def print_result(host, successful, failed, times, availability):
    """Выводит итоговую статистику."""

    print("\n" + "=" * 50)
    print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ ДЛЯ: {host}")
    print("=" * 50)

    print(f"Всего попыток:       {successful + failed}")
    print(f"Успешных попыток:    {successful}")
    print(f"Неуспешных попыток:  {failed}")
    print(f"Доступность:         {availability:.2f}%")

    if times:
        average_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"Среднее RTT:          {average_time:.2f} мс")
        print(f"Минимальное RTT:      {min_time:.2f} мс")
        print(f"Максимальное RTT:     {max_time:.2f} мс")
    else:
        print("Время ответа:         отсутствует")


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("    python icmp_check.py <адрес> [число_попыток]")
        print()
        print("Пример:")
        print("    python icmp_check.py 192.168.1.1 5")
        sys.exit(1)

    host = sys.argv[1]

    if len(sys.argv) >= 3:
        try:
            count = int(sys.argv[2])

            if count <= 0:
                raise ValueError

        except ValueError:
            print("Ошибка: число попыток должно быть положительным целым.")
            sys.exit(1)
    else:
        count = 4

    print("=" * 50)
    print("ПРОВЕРКА ДОСТУПНОСТИ УЗЛА")
    print("=" * 50)
    print(f"Узел: {host}")
    print(f"Количество попыток: {count}")
    print()

    successful, failed, times, availability = ping_host(
        host,
        count
    )

    print_result(
        host,
        successful,
        failed,
        times,
        availability
    )


if __name__ == "__main__":
    main()