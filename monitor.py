import time
import psutil
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        proc = psutil.Process()

        mem_before = proc.memory_info().rss
        cpu_start = proc.cpu_times()

        # Warm up CPU % sampling
        proc.cpu_percent(interval=None)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        cpu_percent = proc.cpu_percent(interval=None)  # % over the last interval
        cpu_end = proc.cpu_times()
        mem_after = proc.memory_info().rss

        cpu_user = cpu_end.user - cpu_start.user
        cpu_system = cpu_end.system - cpu_start.system
        mem_diff = (mem_after - mem_before) / (1024 * 1024)

        print(f"""
=== Performance Log ===
→ PATH: {request.url.path}
→ METHOD: {request.method}
→ Wall Time: {duration:.4f} s
→ CPU Time: User={cpu_user:.4f}s | System={cpu_system:.4f}s
→ Memory Change: {mem_diff:.2f} MB
""")

        return response
