$username = "aws"

$password = aws --profile flyvercity `
    codeartifact get-authorization-token `
    --query authorizationToken `
    --domain flyvercity `
    --domain-owner 368281077578 `
    --region eu-west-3 `
    --output text

Write-Host 'Setting environment variables for CodeArtifact authentication'

$env:UV_INDEX_CODEARTIFACT_USERNAME = $username
$env:UV_INDEX_CODEARTIFACT_PASSWORD = $password
$env:UV_PUBLISH_USERNAME = $username
$env:UV_PUBLISH_PASSWORD = $password
