#!/bin/zsh
# Zip the public site and start an Amplify Hosting job.
# Needs amplify:CreateBranch and amplify:CreateDeployment on this IAM user.
set -euo pipefail
cd "$(dirname "$0")/.."
APP="${AMPLIFY_APP_ID:-d2j18f7hqhja31}"
REGION="${AWS_REGION:-ap-south-1}"
BRANCH="${AMPLIFY_BRANCH:-main}"

rm -rf dist amplify-deploy.zip
mkdir -p dist
cp *.html robots.txt sitemap.xml manifest.webmanifest sw.js dist/
cp -R css js assets dist/
( cd dist && zip -qr ../amplify-deploy.zip . )

if ! aws amplify get-branch --region "$REGION" --app-id "$APP" --branch-name "$BRANCH" >/dev/null 2>&1; then
  aws amplify create-branch --region "$REGION" --app-id "$APP" --branch-name "$BRANCH" --stage PRODUCTION
fi

DEPLOY=$(aws amplify create-deployment --region "$REGION" --app-id "$APP" --branch-name "$BRANCH" --output json)
JOB=$(python3 -c "import json,os; print(json.loads(os.environ['D'])['jobId'])" )
URL=$(python3 -c "import json,os; print(json.loads(os.environ['D'])['zipUploadUrl'])" )
D="$DEPLOY" JOB="$JOB" URL="$URL" python3 - <<'PY'
import json, os
d = json.loads(os.environ["D"])
open("/tmp/knbmf-amplify-job.txt","w").write(d["jobId"]+"\n"+d["zipUploadUrl"])
print("job", d["jobId"])
PY
JOB=$(sed -n '1p' /tmp/knbmf-amplify-job.txt)
URL=$(sed -n '2p' /tmp/knbmf-amplify-job.txt)
curl -sS -X PUT -H "Content-Type: application/zip" --upload-file amplify-deploy.zip "$URL"
aws amplify start-deployment --region "$REGION" --app-id "$APP" --branch-name "$BRANCH" --job-id "$JOB"
echo "https://${BRANCH}.${APP}.amplifyapp.com"
