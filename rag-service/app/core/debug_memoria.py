from time import perf_counter

import psutil

from app.core.config import LOG_MEMORY, LOG_STEP_TIMINGS


def memoria_atual_mb() -> float:
    return psutil.Process().memory_info().rss / (1024 * 1024)


def log_memoria(etapa: str):
    if not LOG_MEMORY:
        return
    uso_mb = memoria_atual_mb()
    print(f"[MEMÓRIA] {etapa}: {uso_mb:.1f} MB")


def log_delta_memoria(etapa: str, memoria_inicial_mb: float):
    if not LOG_MEMORY:
        return
    memoria_final_mb = memoria_atual_mb()
    delta_mb = memoria_final_mb - memoria_inicial_mb
    print(
        f"[MEMÓRIA] {etapa}: {memoria_final_mb:.1f} MB "
        f"(delta {delta_mb:+.1f} MB)"
    )


def log_tempo(etapa: str, inicio: float):
    if not LOG_STEP_TIMINGS:
        return
    duracao = perf_counter() - inicio
    print(f"[TEMPO] {etapa}: {duracao:.2f}s")
