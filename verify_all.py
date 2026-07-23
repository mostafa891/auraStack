import subprocess
import sys


def run_cmd(cmd):
    print(f"Executing: {cmd}")
    try:
        res = subprocess.run(cmd, shell=True, check=True)
        return res.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False


def main():
    print("=== AuraFlow Verification Script ===")

    # 1. Install dependencies
    print("\n--- 1. Installing dependencies ---")
    if not run_cmd(".venv\\Scripts\\python.exe -m pip install -r requirements.txt"):
        print("Dependency installation failed.")
        sys.exit(1)

    # 2. Check migrations
    print("\n--- 2. Checking migrations consistency ---")
    if not run_cmd(".venv\\Scripts\\python.exe manage.py makemigrations --check --dry-run"):
        print("Migrations check failed.")
        sys.exit(1)

    # 3. Run Pytest Suite
    print(
        "\n--- 3. Running pytest suite (including N+1, tenant isolation, lockout, and webhooks) ---"
    )
    if not run_cmd(".venv\\Scripts\\python.exe -m pytest"):
        print("Pytest suite failed.")
        sys.exit(1)

    print("\n=== Success! All verifications passed successfully ===")


if __name__ == "__main__":
    main()
