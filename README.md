 A Security Focused CI/CD Pipeline for a Flask API  (SECDEVOPS Demo)

A demonstration of a security focused CI/CD pipeline built with GitHub Actions. The pipeline tests a small Python Flask application, builds it into a container image, scans the image for vulnerabilities, and publishes it to the GitHub Container Registry (GHCR).

**Overview**

This repository is intentionally simple. The Flask application exists only as a vehicle for the pipeline — the focus of this project is the pipeline itself and the security controls built into it, not the complexity of the app.

The pipeline runs automatically on every push to `main` and consists of two sequential jobs: a `test` job that runs the unit tests, and a `build-scan-push` job that builds the container image, scans it for vulnerabilities, and pushes it to GHCR. The build job only runs if the tests pass.

**Application**

A minimal Flask API with two endpoints, both returning JSON:

- `GET /health` — returns service status and a UTC timestamp
- `GET /info` — returns the application name and version

**Pipeline**

The pipeline is defined in `.github/workflows/pipeline.yml` and triggers on any push to the `main` branch.

### Job 1: `test`

Runs the test before anything is built:

1. Checks out the repository
2. Sets up Python 3.14 
3. Installs dependencies from `requirements.txt`
4. Runs the `pytest` suite against the Flask endpoints

### Job 2: `build-scan-push`

This job declares `needs: test`, so it only runs if the `test` job succeeds. If any test fails, the build is skipped entirely and nothing is published

1. Checks the repo
2. Builds the Docker image from the `Dockerfile`
3. Scans the image with Trivy (fails the pipeline on unpatched CRITICAL/HIGH vulnerabilities)
4. Authenticates to GHCR using the automatically provided `GITHUB_TOKEN`
5. Pushes the image to GHCR

**Security Choices**

The security decisions in this pipeline are deliberate. Each one is explained below:

### Container image scanning with Trivy

The pipeline scans the built image with Trivy and is configured to fail on `CRITICAL` and `HIGH` severity vulnerabilities. This acts as a security measure as a vulnerable image is blocked from being published rather than silently deployed.

### Ignoring unfixed vulnerabilities

Trivy is configured with `ignore-unfixed: true`. On the first run, Trivy flagged 12 CRITICAL/HIGH vulnerabilities in the Debian base layer of the `python:3.14-slim` image, none of which had a patched version available at scan time. Blocking deployment on vulnerabilities with no available fix provides no security benefit, since there is no remediation to apply. With this setting, the pipeline only fails on vulnerabilities that actually have a fix available, the ones a developer can act on. In production, the unfixed vulnerabilities would be tracked in a backlog and the base image updated as patches are released.

### Pinned action versions

All third party GitHub Actions are pinned to specific release versions rather than floating tags like `@master` or `@latest`. This matters: in March 2026, the `aquasecurity/trivy-action` was compromised in a supply chain attack where an attacker force pushed malicious software to existing version tags. Any workflow referencing the action by a mutable tag could have pulled the malicious code. Pinning to a known good version (`v0.35.0`, released after the incident) reduces this risk.

### Authentication with `GITHUB_TOKEN`

The pipeline authenticates to GHCR using the `GITHUB_TOKEN` that GitHub automatically generates for each workflow run. No personal access tokens or long lived credentials are created, stored, or rotated manually. The token is scoped to the repository and expires when the job finishes.

### Minimal base image

The application uses `python:3.14-slim` rather than the full `python:3.14` image. The slim vversion does not include compilers, build tools, and system utilities the application doesn't need at runtime. Fewer packages means a smaller attack surface and fewer potential vulnerabilities for Trivy to find.

### Repository level controls

Beyond the pipeline, the repository has the following enabled:

- **Secret scanning** - detects accidentally committed credentials
- **Dependabot** - alerts on and updates vulnerable dependencies
- **Branch protection on `main`** - requires the Continous Integration pipeline to pass before changes are merged

## Running Locally

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/jdo-connect/sec-cicd-pipeline-demo.git
cd sec-cicd-pipeline-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the app:

```bash
python app/main.py
```

The API will be available at `http://localhost:5000`. Test the endpoints:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/info
```

Run the test suite:

```bash
pytest app/test_main.py -v
```

## Building and Running with Docker

Build the image:

```bash
docker build -t sec-cicd-pipeline-demo .
```

Run the container:

```bash
docker run -d -p 5000:5000 --name flask-app sec-cicd-pipeline-demo
```

## Pulling the Published Image

The image is published to GHCR and can be pulled directly:

```bash
docker pull ghcr.io/jdo-connect/sec-cicd-pipeline-demo:latest
```

## AI Tooling used

This project was built with the assistance of AI tooling for guidance and review, including Claude (specifically Sonnet 4.6 and Opus 4.8) and GitHub Copilot Pro. The code was written in my text editor of choice VScode. 
