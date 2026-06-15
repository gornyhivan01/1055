name: Run Backend and Worker Tests

on:
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component:
          - name: Worker
            path: worker
            requirements: worker/requirements.txt
            test: test_tasks.py
            cov: tasks
          - name: Backend
            path: backend
            requirements: backend/requirements.txt
            test: test_app.py
            cov: backend

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies and security tools
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov bandit

          # Установка Gitleaks (официальный скрипт)
          curl -s https://raw.githubusercontent.com/gitleaks/gitleaks/master/get-gitleaks.sh | sh

          # Установка Trivy (через .deb)
          sudo apt-get update -qq && sudo apt-get install -y wget
          wget -q https://github.com/aquasecurity/trivy/releases/download/v0.53.0/trivy_0.53.0_Linux-64bit.deb
          sudo dpkg -i trivy_0.53.0_Linux-64bit.deb
          trivy --version

      - name: Install component requirements
        run: |
          pip install -r ${{ matrix.component.requirements }}

      # 🛡️ Security scan: Bandit
      - name: Run Bandit security scan
        run: |
          cd ${{ matrix.component.path }} && \
          bandit -r . -f html -o ../../reports/bandit-${{ matrix.component.name }}-report.html \
                 --exclude ./venv,./.venv,./tests,./test_*,./__pycache__,./build,./dist \
                 --exclude ./.git,./.mypy_cache,./.pytest_cache,./.tox || true
        shell: bash

      # 🔑 Security scan: Gitleaks
      - name: Run Gitleaks secret scan
        run: |
          # Убедимся, что gitleaks в PATH
          export PATH="$PATH:$HOME/.gitleaks/bin"
          gitleaks detect --source . --verbose --exit-code 1 --no-color || true
        shell: bash

      # 🛡️ Security scan: Trivy filesystem (только HIGH/CRITICAL)
      - name: Run Trivy filesystem scan
        run: |
          trivy fs --severity HIGH,CRITICAL --exit-code 1 \
                   --skip-dirs .venv,venv,tests,__pycache__,.git \
                   --format json --output ../../reports/trivy-${{ matrix.component.name }}-report.json . || true
        shell: bash

      # 🧪 Run tests
      - name: Run tests
        run: |
          cd ${{ matrix.component.path }} && \
          PYTHONPATH=. python -m pytest ${{ matrix.component.test }} -v --cov=${{ matrix.component.cov }} --cov-report=term

      # 📦 Upload reports
      - name: Upload Bandit report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report-${{ matrix.component.name }}
          path: reports/bandit-${{ matrix.component.name }}-report.html
          retention-days: 7
          if-no-files-found: ignore

      - name: Upload Trivy report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: trivy-report-${{ matrix.component.name }}
          path: reports/trivy-${{ matrix.component.name }}-report.json
          retention-days: 7
          if-no-files-found: ignore