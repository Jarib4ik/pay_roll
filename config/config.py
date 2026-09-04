DEFAULT_BASE_URL = "https://www.example-payroll.dev/"

# Настройки браузера
BROWSER_OPTIONS = {
    "no_sandbox": True,
    "disable_dev_shm_usage": True,
    "disable_extensions": True,
    "disable_gpu": True,
    "ignore_certificate_errors": True,
    "disable_web_security": True,
    "disable_features": "VizDisplayCompositor",
    "no_first_run": True,
    "disable_default_apps": True,
    "disable_popup_blocking": True,
    "disable_translate": True,
    "disable_background_timer_throttling": True,
    "disable_renderer_backgrounding": True,
    "disable_backgrounding_occluded_windows": True,
    "headed": True  # По умолчанию не headless для локальной разработки
}
