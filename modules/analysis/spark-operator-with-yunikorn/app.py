# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os

import aws_cdk
import boto3
from aws_cdk import App

from stack import SparkOperatorWithYuniKornStack

account = os.environ["CDK_DEFAULT_ACCOUNT"]
region = os.environ["CDK_DEFAULT_REGION"]

deployment_name = os.getenv("ADDF_DEPLOYMENT_NAME", "")
module_name = os.getenv("ADDF_MODULE_NAME", "")


def _param(name: str) -> str:
    return f"ADDF_PARAMETER_{name}"


eks_cluster_name = os.getenv(_param("EKS_CLUSTER_NAME"), "")
eks_admin_role_arn = os.getenv(_param("EKS_CLUSTER_ADMIN_ROLE_ARN"), "")
eks_oidc_arn = os.getenv(_param("EKS_OIDC_ARN"), "")

app = App()

stack = SparkOperatorWithYuniKornStack(
    scope=app,
    id=f"addf-{deployment_name}-{module_name}",
    env=aws_cdk.Environment(
        account=account,
        region=region,
    ),
    deployment=deployment_name,
    module=module_name,
    eks_cluster_name=eks_cluster_name,
    eks_admin_role_arn=eks_admin_role_arn,
    eks_oidc_arn=eks_oidc_arn,
)


app.synth(force=True)
