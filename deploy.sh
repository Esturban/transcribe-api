#!/bin/bash

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo -e "${GREEN}Starting Cloud Run deployment...${NC}"

if [[ ! -f .env ]]; then
  echo -e "${RED}Error: .env file not found in $(pwd)${NC}"
  exit 1
fi

set -a
source .env
set +a

required_vars=(PROJECT_ID IMAGE_NAME SERVICE_NAME REGION)
for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo -e "${RED}Error: $var is not set in .env${NC}"
    exit 1
  fi
done

ARTIFACT_REGISTRY_LOCATION="${ARTIFACT_REGISTRY_LOCATION:-$REGION}"
REPOSITORY_PATH="$ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$IMAGE_NAME"
DOCKER_IMAGE="$REPOSITORY_PATH/$IMAGE_NAME"
SMOKE_MDL_PATH="${MDL_PATH:-/usr/src/app/mdl}"
SMOKE_MODEL="${WHISPER_MODEL:-tiny.en}"
TORCH_EXTRA_INDEX_URL="${TORCH_EXTRA_INDEX_URL:-https://download.pytorch.org/whl/cpu}"

echo -e "${BLUE}Configuring Docker authentication for Artifact Registry (${ARTIFACT_REGISTRY_LOCATION})...${NC}"
gcloud auth configure-docker "$ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev"

echo -e "${BLUE}Ensuring Artifact Registry repository '${IMAGE_NAME}' exists...${NC}"
if ! gcloud artifacts repositories describe "$IMAGE_NAME" \
  --location="$ARTIFACT_REGISTRY_LOCATION" \
  --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo -e "${YELLOW}Repository not found. Creating...${NC}"
  gcloud artifacts repositories create "$IMAGE_NAME" \
    --repository-format=docker \
    --location="$ARTIFACT_REGISTRY_LOCATION" \
    --project="$PROJECT_ID" \
    --description="Docker repository for $SERVICE_NAME"
fi

echo -e "${BLUE}Building Docker image ${DOCKER_IMAGE}...${NC}"
BUILD_ARGS=(--build-arg "TORCH_EXTRA_INDEX_URL=${TORCH_EXTRA_INDEX_URL}")
if docker buildx build --platform linux/amd64 -t "$DOCKER_IMAGE" "${BUILD_ARGS[@]}" --load .; then
  echo -e "${GREEN}buildx build completed successfully${NC}"
else
  echo -e "${YELLOW}buildx build failed, falling back to docker build${NC}"
  docker build -t "$DOCKER_IMAGE" "${BUILD_ARGS[@]}" .
fi

if ! docker image inspect "$DOCKER_IMAGE" >/dev/null 2>&1; then
  echo -e "${YELLOW}Local image not found, attempting docker build...${NC}"
  docker build -t "$DOCKER_IMAGE" "${BUILD_ARGS[@]}" .
fi

echo -e "${BLUE}Verifying embedded Whisper model cache...${NC}"
SMOKE_TEST_SCRIPT=$(
  cat <<'PY'
import os
import whisper

mdl = os.environ["MDL_PATH"]
os.makedirs(mdl, exist_ok=True)
whisper.load_model(os.environ["WHISPER_MODEL"], download_root=mdl)
PY
)

docker run --rm \
  -e WHISPER_MODEL="$SMOKE_MODEL" \
  -e MDL_PATH="$SMOKE_MDL_PATH" \
  --entrypoint python \
  "$DOCKER_IMAGE" \
  -c "$SMOKE_TEST_SCRIPT" >/dev/null

echo -e "${BLUE}Pushing image to Artifact Registry...${NC}"
docker push "$DOCKER_IMAGE"

echo -e "${BLUE}Collecting runtime environment variables from .env...${NC}"
ENV_VARS=()
while IFS= read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  [[ "$line" != *=* ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  key="$(echo "$key" | xargs)"
  [[ -z "$key" ]] && continue
  case "$key" in
    PROJECT_ID|IMAGE_NAME|SERVICE_NAME|REGION|ARTIFACT_REGISTRY_LOCATION)
      continue
      ;;
  esac
  value="$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/'/'\"'\"'/g")"
  ENV_VARS+=("$key=$value")
done < .env

ENV_FLAG=()
if [[ ${#ENV_VARS[@]} -gt 0 ]]; then
  joined_env_vars="$(IFS=','; echo "${ENV_VARS[*]}")"
  ENV_FLAG=(--set-env-vars "$joined_env_vars")
fi

API_PORT_VALUE="${API_PORT:-8000}"

echo -e "${BLUE}Deploying service ${SERVICE_NAME} to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
  --image "$DOCKER_IMAGE" \
  --project "$PROJECT_ID" \
  --platform managed \
  --region "$REGION" \
  --port "$API_PORT_VALUE" \
  --allow-unauthenticated \
  "${ENV_FLAG[@]}"

echo -e "${GREEN}Deployment completed successfully!${NC}"

