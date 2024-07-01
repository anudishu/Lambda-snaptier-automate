# Lambda-snaptier-automate

# Lambda Snapshot Tier Automation

This AWS Lambda script automates the process of creating EBS snapshots, changing their storage tiers, and eventually deleting the snapshots. This can help optimize storage costs and ensure that your snapshots are managed efficiently.

## Features

- **Automated Snapshot Creation:** Automatically create snapshots of specified EBS volumes.
- **Tier Change:** Change the storage tier of snapshots to optimize costs.
- **Automated Deletion:** Automatically delete snapshots after a specified retention period.

## Prerequisites

- **AWS Account:** An active AWS account with appropriate permissions.
- **AWS Lambda:** Ensure you have AWS Lambda enabled in your AWS account.
- **IAM Role:** An IAM role with the following permissions:
  - `ec2:CreateSnapshot`
  - `ec2:ModifySnapshotAttribute`
  - `ec2:DeleteSnapshot`
  - `ec2:DescribeSnapshots`
  - `ec2:DescribeVolumes`


