FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY zil_interpreter/ ./zil_interpreter/
RUN pip install --no-cache-dir -e .

# Copy game source
COPY zork1/ ./zork1/

# Default: run Zork I in JSON mode (for UI integration)
# Override CMD to use interactive mode: docker run -it zork1 python -m zil_interpreter zork1/zork1.zil
ENTRYPOINT ["python", "-m", "zil_interpreter"]
CMD ["zork1/zork1.zil", "--json"]
