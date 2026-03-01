import random
from multiprocessing import Pool, cpu_count

import numpy as np
from numpy import uint8
from PIL import Image

from logger import logger
from transformations import TRANSFORMATIONS


def _worker_chunk(args: tuple) -> tuple:
    iterations, affine_transforms, function_weights, width, height, seed, worker_id = (
        args
    )
    """Генерирует итерации в отдельном процессе."""
    random.seed(seed + worker_id)

    hist_r = np.zeros((height, width), dtype=np.float64)
    hist_g = np.zeros((height, width), dtype=np.float64)
    hist_b = np.zeros((height, width), dtype=np.float64)
    hist_freq = np.zeros((height, width), dtype=np.float64)

    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)

    func_names = list(function_weights.keys())
    weights = list(function_weights.values())

    for _ in range(iterations):
        affine = random.choice(affine_transforms)

        a = affine["a"]
        b = affine["b"]
        c = affine["c"]
        d = affine["d"]
        e = affine["e"]
        f = affine["f"]

        new_x = a * x + b * y + c
        new_y = d * x + e * y + f
        x, y = new_x, new_y

        func_name = random.choices(func_names, weights=weights)[0]
        variation_func = TRANSFORMATIONS[func_name]
        x, y = variation_func(x, y)

        px = int((x + 1.0) / 2.0 * width)
        py = int((y + 1.0) / 2.0 * height)

        if 0 <= px < width and 0 <= py < height:
            color = affine["color"]
            hist_r[py, px] += color[0]
            hist_g[py, px] += color[1]
            hist_b[py, px] += color[2]
            hist_freq[py, px] += 1

    return hist_r, hist_g, hist_b, hist_freq


class FlameGenerator:
    """Генератор фрактального пламени."""

    def __init__(self, width: int, height: int, iterations: int, seed: float) -> None:
        """Инициализация генератора."""
        self.width = width
        self.height = height
        self.iterations = iterations
        self.seed = seed
        self.threads = 1

    def set_threads(self, threads: int) -> None:
        """Устанавливает кол-во потоков."""
        threads = max(threads, 1)

        max_threads = cpu_count()
        if threads > max_threads:
            logger.warning("Потоков больше, чем ядер.")
            threads = max_threads

        self.threads = threads

    def _create_histograms(self) -> tuple:
        """Создаем нулевые гистограммы."""
        hist_r = np.zeros((self.height, self.width))
        hist_g = np.zeros((self.height, self.width))
        hist_b = np.zeros((self.height, self.width))
        hist_freq = np.zeros((self.height, self.width))

        return hist_r, hist_g, hist_b, hist_freq

    @staticmethod
    def _apply_affine_transform(
        x: float, y: float, affine: dict[str, float]
    ) -> tuple[float, float]:
        """Применяем афинное преобразование к точке."""
        a = affine["a"]
        b = affine["b"]
        c = affine["c"]
        d = affine["d"]
        e = affine["e"]
        f = affine["f"]

        new_x = a * x + b * y + c
        new_y = d * x + e * y + f

        return new_x, new_y

    def _chaos_game_loop(
        self,
        affine_transforms: list[dict],
        function_weights: dict[str, float],
        hist_r: np.ndarray,
        hist_g: np.ndarray,
        hist_b: np.ndarray,
        hist_freq: np.ndarray,
    ) -> None:
        """Генерирует точки в однопоточном режиме."""
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)

        func_names = list(function_weights.keys())
        weights = list(function_weights.values())

        for _iteration in range(self.iterations):

            affine = random.choice(affine_transforms)
            x, y = self._apply_affine_transform(x, y, affine)
            func_name = random.choices(func_names, weights=weights)[0]
            variation_func = TRANSFORMATIONS[func_name]
            x, y = variation_func(x, y)

            px = int((x + 1.0) / 2.0 * self.width)
            py = int((y + 1.0) / 2.0 * self.height)

            if 0 <= px < self.width and 0 <= py < self.height:
                color = affine["color"]
                hist_r[py][px] += color[0]
                hist_g[py][px] += color[1]
                hist_b[py][px] += color[2]
                hist_freq[py][px] += 1

    def _process_histograms(self, hist_freq: np.ndarray) -> np.ndarray:
        """Обработка гистограммы частоты."""
        log_freq = np.log(hist_freq + 1)
        max_log = np.max(log_freq)
        return log_freq / max_log if max_log > 0 else np.zeros_like(log_freq)

    def _histograms_to_rgb(
        self,
        hist_r: np.ndarray,
        hist_g: np.ndarray,
        hist_b: np.ndarray,
        hist_freq: np.ndarray,
        intensity: np.ndarray,
    ) -> np.ndarray:
        """Преобразует гистограммы в формат RGB."""
        img_array = np.zeros((self.height, self.width, 3), dtype=uint8)

        for y in range(self.height):
            for x in range(self.width):
                if hist_freq[y, x] > 0:
                    r = hist_r[y, x] / hist_freq[y, x] * intensity[y, x]
                    g = hist_g[y, x] / hist_freq[y, x] * intensity[y, x]
                    b = hist_b[y, x] / hist_freq[y, x] * intensity[y, x]

                    img_array[y, x, 0] = min(255, int(r * 255))
                    img_array[y, x, 1] = min(255, int(g * 255))
                    img_array[y, x, 2] = min(255, int(b * 255))
                else:
                    img_array[y, x] = [0, 0, 0]

        return img_array

    def _save_image(self, img_array: np.ndarray, output_path: str) -> None:
        """Сохраняем изображение в файл."""
        img = Image.fromarray(img_array, mode="RGB")
        img.save(output_path)

    def _merge_results(self, results: list) -> tuple:
        """Объединяет результаты от всех рабочих процессов."""
        hist_r, hist_g, hist_b, hist_freq = self._create_histograms()
        for worker_r, worker_g, worker_b, worker_freq in results:
            hist_r += worker_r
            hist_g += worker_g
            hist_b += worker_b
            hist_freq += worker_freq
        return hist_r, hist_g, hist_b, hist_freq

    def generate(
        self,
        affine_transforms: list[dict],
        function_weights: dict[str, float],
        output_path: str,
    ) -> None:
        """Генерирует пламя и сохраняет."""
        if self.threads == 1:
            hist_r, hist_g, hist_b, hist_freq = self._create_histograms()
            self._chaos_game_loop(
                affine_transforms, function_weights, hist_r, hist_g, hist_b, hist_freq
            )
        else:
            iter_per_worker = self.iterations // self.threads
            worker_args = []
            for worker_id in range(self.threads):
                if worker_id == self.threads - 1:
                    chunk_iters = self.iterations - worker_id * iter_per_worker
                else:
                    chunk_iters = iter_per_worker

                worker_args.append(
                    (
                        chunk_iters,
                        affine_transforms,
                        function_weights,
                        self.width,
                        self.height,
                        self.seed,
                        worker_id,
                    )
                )
            with Pool(processes=self.threads) as pool:
                results = pool.map(_worker_chunk, worker_args)

            hist_r, hist_g, hist_b, hist_freq = self._create_histograms()
            for r, g, b, f in results:
                hist_r += r
                hist_g += g
                hist_b += b
                hist_freq += f

        intensity = self._process_histograms(hist_freq)
        img_array = self._histograms_to_rgb(
            hist_r, hist_g, hist_b, hist_freq, intensity
        )
        self._save_image(img_array, output_path)
