# Troubleshooting (WIP)

Q. When I try to run `docker-compose up` I get the error: "configs.qdrant_config Additional property content is not allowed"

A. Proving the inline content in the configs top-level element requires Docker Compose v2.23.1 or above. This functionality is supported starting Docker Engine v25.0.0 and Docker Desktop v4.26.0 onwards.
