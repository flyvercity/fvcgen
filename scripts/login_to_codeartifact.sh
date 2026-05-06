#!/bin/bash
# Source this script: . ./scripts/login_to_codeartifact.sh

USERNAME="aws"

PASSWORD=$(aws --profile flyvercity \
    codeartifact get-authorization-token \
    --query authorizationToken \
    --domain flyvercity \
    --domain-owner 368281077578 \
    --region eu-west-3 \
    --output text)

echo 'Setting environment variables for CodeArtifact authentication'

export UV_INDEX_CODEARTIFACT_USERNAME="$USERNAME"
export UV_INDEX_CODEARTIFACT_PASSWORD="$PASSWORD"
export UV_PUBLISH_USERNAME="$USERNAME"
export UV_PUBLISH_PASSWORD="$PASSWORD"
