# Bamboo 12.1 — GET エンドポイント全一覧

公式 swagger（12.1.0）から機械生成。パスは swagger 表記（先頭は `/rest` が付く。実際の URL は `{ベースURL}/rest` + このパス）。
GET は全 208 件。スキルは GET のみを使う。スコープは OAuth2 注記で、WRITE とある GET は読み取り専用トークンでは 403 になり得る。

## access-token

- `GET /api/latest/access-token`（-）

## admin

- `GET /api/latest/admin/expiry/custom/plan`（WRITE）
- `GET /api/latest/admin/groups`（-）
- `GET /api/latest/admin/groups/{name}/more-members`（-）
- `GET /api/latest/admin/groups/{name}/more-non-members`（-）
- `GET /api/latest/admin/users`（-）
- `GET /api/latest/admin/users/{name}/access-token`（-）
- `GET /api/latest/admin/users/{name}/alias`（-）
- `GET /api/latest/admin/users/{name}/assigned-groups`（-）
- `GET /api/latest/admin/users/{name}/unassigned-aliases`（-）
- `GET /api/latest/admin/users/{name}/unassigned-groups`（-）

## agent

- `GET /api/latest/agent`（-）
- `GET /api/latest/agent/assignment`（-）
- `GET /api/latest/agent/assignment/search`（-）
- `GET /api/latest/agent/authentication`（-）
- `GET /api/latest/agent/remote`（-）
- `GET /api/latest/agent/{agentId}`（-）
- `GET /api/latest/agent/{agentId}/capability`（-）
- `GET /api/latest/agent/{agentId}/status`（-）

## artifactHandlers

- `GET /admin/latest/artifactHandlers/agentLocal`（-）
- `GET /admin/latest/artifactHandlers/bambooRemote`（-）
- `GET /admin/latest/artifactHandlers/s3`（-）
- `GET /admin/latest/artifactHandlers/sftp`（-）

## avatar

- `GET /api/latest/avatar/user/{userName}/avatar.png`（READ）

## brokenBuild

- `GET /responsibility/latest/brokenBuild/byUser/{name}`（-）
- `GET /responsibility/latest/brokenBuild/myBrokenBuilds`（-）
- `GET /responsibility/latest/brokenBuild/{planResultKeyOrPlanKey}`（READ）

## buildNumber

- `GET /api/latest/buildNumber/{projectKey}-{buildKey}`（READ）

## capability

- `GET /api/latest/capability/groupedListing`（READ）

## chart

- `GET /api/latest/chart`（READ）
- `GET /api/latest/chart/planSummary`（READ）
- `GET /api/latest/chart/reports`（READ）

## config

- `GET /admin/latest/config/agents`（-）
- `GET /admin/latest/config/agents/offlineAgentRemoval`（-）
- `GET /admin/latest/config/agents/{agentId}`（-）
- `GET /admin/latest/config/auditLog`（-）
- `GET /admin/latest/config/build/concurrency`（-）
- `GET /admin/latest/config/build/monitoring`（-）
- `GET /admin/latest/config/general`（-）
- `GET /admin/latest/config/imServer`（-）
- `GET /admin/latest/config/mailServer`（-）
- `GET /admin/latest/config/quarantine`（-）
- `GET /admin/latest/config/remoteAgentSupport`（-）
- `GET /api/latest/config/job/{jobKey}/agent-assignment`（WRITE）
- `GET /api/latest/config/job/{jobKey}/agent-assignment/possible-agent-assignment`（WRITE）

## currentUser

- `GET /api/latest/currentUser`（-）

## darkFeatures

- `GET /admin/latest/darkFeatures`（-）
- `GET /admin/latest/darkFeatures/{key}`（-）
- `GET /admin/latest/darkFeatures/{key}/user/{userName}`（-）

## dependency

- `GET /api/latest/dependency/search/{projectKey}-{buildKey}/child`（WRITE）
- `GET /api/latest/dependency/search/{projectKey}-{buildKey}/parent`（WRITE）

## deploy

- `GET /api/latest/deploy/dashboard`（READ）
- `GET /api/latest/deploy/dashboard/paginate`（READ）
- `GET /api/latest/deploy/dashboard/paginate/{projectId}`（READ）
- `GET /api/latest/deploy/dashboard/{projectId}`（READ）
- `GET /api/latest/deploy/environment/agent/{agentId}`（-）
- `GET /api/latest/deploy/environment/elasticImageConfiguration/{configurationId}`（-）
- `GET /api/latest/deploy/environment/ephemeral/{templateId}`（-）
- `GET /api/latest/deploy/environment/{environmentId}`（READ）
- `GET /api/latest/deploy/environment/{environmentId}/agent-assignment`（-）
- `GET /api/latest/deploy/environment/{environmentId}/docker`（WRITE）
- `GET /api/latest/deploy/environment/{environmentId}/possible-agent-assignment`（-）
- `GET /api/latest/deploy/environment/{environmentId}/requirement`（WRITE）
- `GET /api/latest/deploy/environment/{environmentId}/requirement/detailedSummary`（WRITE）
- `GET /api/latest/deploy/environment/{environmentId}/requirement/summary`（WRITE）
- `GET /api/latest/deploy/environment/{environmentId}/requirement/{requirementId}`（WRITE）
- `GET /api/latest/deploy/environment/{environmentId}/results`（READ）
- `GET /api/latest/deploy/environment/{environmentId}/variable/{variableName}`（READ）
- `GET /api/latest/deploy/environment/{environmentId}/variables`（READ）
- `GET /api/latest/deploy/issue-status/{issueKey}`（READ）
- `GET /api/latest/deploy/issue-status/{issueKey}/{deploymentProjectId}`（READ）
- `GET /api/latest/deploy/preview/possibleResults`（READ）
- `GET /api/latest/deploy/preview/result`（READ）
- `GET /api/latest/deploy/preview/version`（READ）
- `GET /api/latest/deploy/preview/versionName`（READ）
- `GET /api/latest/deploy/project/all`（READ）
- `GET /api/latest/deploy/project/forPlan`（READ）
- `GET /api/latest/deploy/project/{deploymentProjectId}`（READ）
- `GET /api/latest/deploy/project/{deploymentProjectId}/repository`（READ）
- `GET /api/latest/deploy/project/{deploymentProjectId}/repository/search`（READ）
- `GET /api/latest/deploy/project/{deploymentProjectId}/specs`（WRITE）
- `GET /api/latest/deploy/project/{deploymentProjectId}/version`（READ）
- `GET /api/latest/deploy/project/{deploymentProjectId}/versions`（-）
- `GET /api/latest/deploy/projectVersioning/{deploymentProjectId}/namingPreview`（READ）
- `GET /api/latest/deploy/projectVersioning/{deploymentProjectId}/nextVersion`（READ）
- `GET /api/latest/deploy/projectVersioning/{deploymentProjectId}/parseVariables`（READ）
- `GET /api/latest/deploy/projectVersioning/{deploymentProjectId}/variables`（READ）
- `GET /api/latest/deploy/result/{deploymentResultId}`（READ）
- `GET /api/latest/deploy/version/{deploymentVersionId}/build-result`（READ）
- `GET /api/latest/deploy/version/{deploymentVersionId}/status`（READ）

## elastic

- `GET /admin/latest/elastic/config`（-）

## elasticConfiguration

- `GET /api/latest/elasticConfiguration`（-）
- `GET /api/latest/elasticConfiguration/{configurationId}`（-）

## elasticInstances

- `GET /api/latest/elasticInstances/instance/{instanceId}/logs`（-）

## ephemeral

- `GET /admin/latest/ephemeral/config`（-）
- `GET /api/latest/ephemeral/pod/{pod}/logs`（-）
- `GET /api/latest/ephemeral/pod/{pod}/logs/raw`（-）
- `GET /api/latest/ephemeral/templateConfiguration`（-）
- `GET /api/latest/ephemeral/templateConfiguration/{configurationId}`（-）
- `GET /api/latest/ephemeral/templateConfiguration/{configurationId}/capability`（-）

## expiry

- `GET /admin/latest/expiry/configuration`（-）
- `GET /admin/latest/expiry/status`（-）

## globalVariables

- `GET /admin/latest/globalVariables`（-）
- `GET /admin/latest/globalVariables/{variableId}`（-）

## info

- `GET /api/latest/info`（READ）

## job

- `GET /api/latest/job/{jobKey}/docker`（WRITE）

## latest

- `GET /api/latest/`（READ）

## permissions

- `GET /api/latest/permissions/deployment/{id}/available-groups`（WRITE）
- `GET /api/latest/permissions/deployment/{id}/available-users`（WRITE）
- `GET /api/latest/permissions/deployment/{id}/groups`（WRITE）
- `GET /api/latest/permissions/deployment/{id}/roles`（WRITE）
- `GET /api/latest/permissions/deployment/{id}/users`（WRITE）
- `GET /api/latest/permissions/environment/{id}/available-groups`（WRITE）
- `GET /api/latest/permissions/environment/{id}/available-users`（WRITE）
- `GET /api/latest/permissions/environment/{id}/groups`（WRITE）
- `GET /api/latest/permissions/environment/{id}/roles`（WRITE）
- `GET /api/latest/permissions/environment/{id}/users`（WRITE）
- `GET /api/latest/permissions/global/available-groups`（-）
- `GET /api/latest/permissions/global/available-users`（-）
- `GET /api/latest/permissions/global/groups`（-）
- `GET /api/latest/permissions/global/roles`（-）
- `GET /api/latest/permissions/global/users`（-）
- `GET /api/latest/permissions/plan/{key}/available-groups`（WRITE）
- `GET /api/latest/permissions/plan/{key}/available-users`（WRITE）
- `GET /api/latest/permissions/plan/{key}/groups`（WRITE）
- `GET /api/latest/permissions/plan/{key}/roles`（WRITE）
- `GET /api/latest/permissions/plan/{key}/users`（WRITE）
- `GET /api/latest/permissions/project/{key}/available-groups`（WRITE）
- `GET /api/latest/permissions/project/{key}/available-users`（WRITE）
- `GET /api/latest/permissions/project/{key}/groups`（WRITE）
- `GET /api/latest/permissions/project/{key}/roles`（WRITE）
- `GET /api/latest/permissions/project/{key}/users`（WRITE）
- `GET /api/latest/permissions/projectplan/{key}/available-groups`（WRITE）
- `GET /api/latest/permissions/projectplan/{key}/available-users`（WRITE）
- `GET /api/latest/permissions/projectplan/{key}/groups`（WRITE）
- `GET /api/latest/permissions/projectplan/{key}/roles`（WRITE）
- `GET /api/latest/permissions/projectplan/{key}/users`（WRITE）
- `GET /api/latest/permissions/repository/{id}/available-groups`（WRITE）
- `GET /api/latest/permissions/repository/{id}/available-users`（WRITE）
- `GET /api/latest/permissions/repository/{id}/groups`（WRITE）
- `GET /api/latest/permissions/repository/{id}/roles`（WRITE）
- `GET /api/latest/permissions/repository/{id}/users`（WRITE）

## plan

- `GET /api/latest/plan`（READ）
- `GET /api/latest/plan/favicon/{planKey}`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/artifact`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/branch`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/branch/{branchName}`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/issue/{issueKey}`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/label`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/specs`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/variables`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/variables/{variableName}`（READ）
- `GET /api/latest/plan/{projectKey}-{buildKey}/vcsBranches`（READ）
- `GET /api/latest/plan/{projectKey}/{buildKey}`（READ）

## planDirectoryInfo

- `GET /api/latest/planDirectoryInfo/{planKey}`（READ）

## project

- `GET /api/latest/project`（READ）
- `GET /api/latest/project/{projectKey}`（READ）
- `GET /api/latest/project/{projectKey}/repositories`（READ）
- `GET /api/latest/project/{projectKey}/repository`（READ）
- `GET /api/latest/project/{projectKey}/repository/search`（READ）
- `GET /api/latest/project/{projectKey}/sharedCredentials`（READ）
- `GET /api/latest/project/{projectKey}/specs`（READ）
- `GET /api/latest/project/{projectKey}/variable/{variableName}`（READ）
- `GET /api/latest/project/{projectKey}/variables`（READ）

## queue

- `GET /api/latest/queue`（READ）
- `GET /api/latest/queue/deployment`（READ）

## quickFilter

- `GET /api/latest/quickFilter`（READ）
- `GET /api/latest/quickFilter/active`（READ）
- `GET /api/latest/quickFilter/visible`（READ）
- `GET /api/latest/quickFilter/{id}`（READ）

## quicksearch

- `GET /api/latest/quicksearch`（READ）

## reindex

- `GET /api/latest/reindex`（-）

## repository

- `GET /api/latest/repository`（READ）
- `GET /api/latest/repository/{repositoryId}/rssBranches`（READ）
- `GET /api/latest/repository/{repositoryId}/rssrepository`（WRITE）
- `GET /api/latest/repository/{repositoryId}/rssrepository/search`（WRITE）
- `GET /api/latest/repository/{repositoryId}/scan/status`（READ）
- `GET /api/latest/repository/{repositoryId}/usage`（READ）

## result

- `GET /api/latest/result`（READ）
- `GET /api/latest/result/byChangeset/{csid}`（READ）
- `GET /api/latest/result/byCheckoutChangeset/{csid}`（READ）
- `GET /api/latest/result/status/{projectKey}-{buildKey}-{buildNumber}`（READ）
- `GET /api/latest/result/{projectKey}`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}-{buildNumber}`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}-{buildNumber}/comment`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}-{buildNumber}/label`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}/branch/{branchName}`（READ）
- `GET /api/latest/result/{projectKey}-{buildKey}/{buildNumber}`（READ）

## scheduler

- `GET /admin/latest/scheduler/jobs`（-）

## search

- `GET /api/latest/search/authors`（READ）
- `GET /api/latest/search/branches`（READ）
- `GET /api/latest/search/deployments`（READ）
- `GET /api/latest/search/jobs/{planKey}`（READ）
- `GET /api/latest/search/plans`（READ）
- `GET /api/latest/search/projects`（READ）
- `GET /api/latest/search/stages/{planKey}`（READ）
- `GET /api/latest/search/users`（READ）
- `GET /api/latest/search/versions`（READ）

## security

- `GET /admin/latest/security/groups`（-）
- `GET /admin/latest/security/settings`（-）
- `GET /admin/latest/security/trustedKey`（-）

## server

- `GET /api/latest/server`（READ）
- `GET /api/latest/server/nodes`（-）

## status

- `GET /api/latest/status`（READ）

## systemInfo

- `GET /admin/latest/systemInfo`（-）

## websudo-session

- `GET /api/latest/websudo-session`（-）
