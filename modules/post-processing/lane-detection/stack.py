# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, cast

import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
from aws_cdk import Duration, Stack, Tags
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class LaneDetection(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        deployment_name: str,
        module_name: str,
        s3_access_policy: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            scope,
            id,
            **kwargs,
        )

        Tags.of(scope=cast(IConstruct, self)).add(
            key="Deployment",
            value="aws",
        )

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"

        self.repository_name = dep_mod
        repo = ecr.Repository(self, id=self.repository_name, repository_name=self.repository_name)
        self.image_uri = f"{repo.repository_uri}:smprocessor"

        policy_statements = [
            iam.PolicyStatement(
                actions=["dynamodb:*"],
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/{project_name}*"],
            ),
            iam.PolicyStatement(
                actions=["ecr:*"],
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:ecr:{self.region}:{self.account}:repository/{dep_mod}*"],
            ),
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:GetObjectAcl", "s3:ListBucket"],
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:s3:::{project_name}-*", f"arn:aws:s3:::{project_name}-*/*"],
            ),
        ]
        dag_document = iam.PolicyDocument(statements=policy_statements)

        self.role = iam.Role(
            self,
            f"{self.repository_name}-sm-role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("sagemaker.amazonaws.com"),
            ),
            inline_policies={"DagPolicyDocument": dag_document},
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                iam.ManagedPolicy.from_managed_policy_arn(self, id="fullaccess", managed_policy_arn=s3_access_policy),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
            ],
            max_session_duration=Duration.hours(12),
        )
