import numpy as np
import string
from typing import List, Optional

# Генерация псевдослучайного массива по сиду
def generate_random_array(seed: int, length: int, max_value: int = 255) -> List[int]:
    """Возвращает список int в диапазоне [0, max_value] длины length, детерминированный seed."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, max_value + 1, size=length).tolist()


def decode_from_array(arr: List[int]) -> Optional[str]:
    """Пытается декодировать массив в текст, используя ту же логику разделителя (sdf = max(arr)-10).

    Возвращает строку (возможно с символами '?') если разделитель найден, иначе None.
    """
    if not arr:
        return None

    sdf = max(arr) - 10
    # Найдём позиции-разделители (значения == sdf)
    sep_positions = [i for i, v in enumerate(arr) if v == sdf]
    if not sep_positions:
        return None

    # Разбиваем по разделителям, исключая сами разделители
    segments = []
    prev = 0
    for p in sep_positions:
        segments.append(arr[prev:p])
        prev = p + 1
    if prev < len(arr):
        segments.append(arr[prev:])

    # Удалим пустые сегменты
    segments = [seg for seg in segments if seg]
    if not segments:
        return None

    # Первый сегмент — коды символов
    symbol_codes = segments[0]
    try:
        symbols = [chr(int(c)) for c in symbol_codes]
    except Exception:
        # Некорректные коды
        return None

    index_lists = segments[1:]

    # Если нет списков индексов — просто вернём строку из символов
    if not index_lists:
        return ''.join(symbols)

    # Определим размер результата по максимальному индексу
    try:
        max_index = max((max(lst) for lst in index_lists if lst), default=-1)
    except ValueError:
        return None

    if max_index < 0:
        return ''.join(symbols)

    result = ['?' for _ in range(max_index + 1)]

    # Заполним результат символами по индексам
    for sym, idxs in zip(symbols, index_lists):
        for idx in idxs:
            if idx is None:
                continue
            if idx < 0:
                continue
            # Безопасно расширим, если вдруг индекс больше ожидаемого
            if idx >= len(result):
                result.extend('?' * (idx - len(result) + 1))
            result[idx] = sym

    return ''.join(result)


def is_mostly_printable(s: str, threshold: float = 0.95) -> bool:
    """Проверяет, являются ли символы в строке в основном печатными (ASCII printable).
    threshold — доля печатных символов для прохождения фильтра."""
    if not s:
        return False
    printable_count = sum(1 for ch in s if ch in string.printable)
    return (printable_count / len(s)) >= threshold


def search_from_seed(start_seed: int, rainbow_row: int, array_length: int, max_value: int = 255):
    """Перебирает сиды от start_seed до start_seed+rainbow_row-1 и пытается декодировать сгенерированные массивы."""
    for seed in range(start_seed, start_seed + rainbow_row):
        arr = generate_random_array(seed, array_length, max_value)
        decoded = decode_from_array(arr)
        if decoded is None:
            print(f"seed={seed}: разделитель (sdf) не найден или декодирование не удалось")
        else:
            printable = is_mostly_printable(decoded)
            status = "[ПРОХОДИТ ФИЛЬТР]" if printable else "[непечатные символы]"
            print(f"seed={seed} {status}: {decoded}")


if __name__ == '__main__':
    # Параметры — подберите под вашу задачу
    start_seed = 9          # starting_seed
    rainbow_row = 20        # сколько последовательных сидов проверить
    array_length = 220      # длина генерируемого массива (подставьте нужное значение)
    max_value = 180         # максимальное значение в массиве (по умолчанию 255)

    # Запуск поиска
    search_from_seed(start_seed, rainbow_row, array_length, max_value)
