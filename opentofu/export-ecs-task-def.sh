#!/bin/bash
set -euo pipefail

# Generate the OpenTofu state as JSON
tofu show -json > opentofu/terraform-state.json

# Extract the ECS task definition and write to ecs-task-def.json
jq -r '
  .values.root_module.resources[]
  | select(.type == "aws_ecs_task_definition" and .name == "app")
  | {
      family: .values.family,
      networkMode: .values.network_mode,
      requiresCompatibilities: .values.requires_compatibilities,
      cpu: .values.cpu,
      memory: .values.memory,
      executionRoleArn: .values.execution_role_arn,
      containerDefinitions: (.values.container_definitions | fromjson)
    }
' opentofu/terraform-state.json > opentofu/ecs-task-def.json