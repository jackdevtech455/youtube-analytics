from yta_worker.settings import WorkerSettings
from yta_worker.services.worker_loop import run_worker_loop

def main() -> None:
    worker_settings = WorkerSettings()
    print("[worker] starting...", flush=True)
    run_worker_loop(worker_settings)

if __name__ == "__main__":
    main()
