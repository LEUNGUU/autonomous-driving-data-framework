# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
from typing import Any, cast

import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from aws_cdk import aws_eks as eks
from aws_cdk import aws_iam as iam
from cdk_nag import NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)

# project_dir = os.path.dirname(os.path.abspath(__file__))


class SparkOperatorWithYuniKornStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        deployment: str,
        module: str,
        eks_cluster_name: str,
        eks_admin_role_arn: str,
        eks_oidc_arn: str,
        **kwargs: Any,
    ) -> None:

        super().__init__(
            scope,
            id,
            description="This stack deploys spark operator with yunikorn",
            **kwargs,
        )

        Tags.of(scope=cast(IConstruct, self)).add(
            key="Deployment",
            value=f"addf-{deployment}",
        )

        dep_mod = f"addf-{deployment}-{module}"

        # Import EKS Cluster
        provider = eks.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self, f"{dep_mod}-provider", eks_oidc_arn
        )
        eks_cluster = eks.Cluster.from_cluster_attributes(
            self,
            f"{dep_mod}-eks-cluster",
            cluster_name=eks_cluster_name,
            kubectl_role_arn=eks_admin_role_arn,
            open_id_connect_provider=provider,
        )

        # Create spark-operator namespace
        # spark_operator_namespace = eks_cluster.add_manifest(
        #     "spark-operator-namespace",
        #     {
        #         "apiVersion": "v1",
        #         "kind": "Namespace",
        #         "metadata": {"name": "spark-operator"},
        #     },
        # )
        #
        # spark_operator_service_account = eks_cluster.add_service_account(
        #     "spark-operator-service-account",
        #     name="spark-operator",
        #     namespace="spark-operator",
        # )

        k8s_value = {
            "replicaCount": 1,
            "webhook": {"enable": True, "port": 8080},
            "serviceAccounts": {
                "spark": {"create": True, "name": "apps", "annotations": {}},
                "sparkoperator": {"create": True, "name": "", "annotations": {}},
            },
            "controllerThreads": 10,
            "resources": {
                "limits": {"cpu": "200m", "memory": "1Gi"},
                "requests": {"cpu": "100m", "memory": "512Mi"},
            },
            "batchScheduler": {"enable": True},
            "uiService": {"enable": True},
        }

        spark_operator_chart = eks_cluster.add_helm_chart(
            "spark-operator-chart",
            chart="spark-operator",
            release="spark-operator",
            repository="https://kubeflow.github.io/spark-operator",
            namespace="spark-operator",
            create_namespace=True,
            values=k8s_value,
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
