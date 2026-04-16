def get_status(noise: float) -> str:
    if noise < 0.35:
        return "stable"
    if noise < 0.6:
        return "warning"
    return "degraded"
