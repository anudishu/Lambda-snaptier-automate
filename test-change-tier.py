# This script is also good. it send email in nice format. tested.
import boto3
import datetime
from botocore.exceptions import ClientError

# Create an SNS client
sns_client = boto3.client('sns')
ec2 = boto3.client('ec2')

# Set the SNS topic ARN
sns_topic_arn = "<replace with your SNS Topic ARN"

# Get the current date in YYYY-MM-DD format
currentDate = datetime.datetime.now().strftime("%Y-%m-%d")

# Initialize an empty list to store snapshot details
snaplist = []

def lambda_handler(event, context):
    # Create a filter to find snapshots with tag key ArchiveOn and value current date
    filters = [
        {
            'Name': 'tag:ArchiveOn',
            'Values': [
                currentDate,
            ],
        },
    ]

    # Get the list of snapshots matching the filter
    paginator = ec2.get_paginator('describe_snapshots')
    response_iterator = paginator.paginate(
        Filters=filters,
    )

    # Iterate over the snapshots and process them
    for obj in response_iterator:
        for snap in obj['Snapshots']:
            snapshot_id = snap['SnapshotId']
            snapshot_name = snap.get('Description', 'N/A')

            snaplist.append({
                'SnapshotId': snapshot_id,
                'SnapshotName': snapshot_name,
            })

            # Archive the snapshot
            try:
                archivesnap = ec2.modify_snapshot_tier(
                    SnapshotId=snapshot_id,
                    StorageTier='archive',
                    # DryRun=True # Uncomment this line to test without archiving
                )
                print("Archived snapshot id {}".format(snapshot_id))
            except ClientError as e:
                print(e.response['Error']['Message'])

    # Prepare the email message
    subject = "List of Snapshots to Archive on {}".format(currentDate)
    body = "The following snapshots are scheduled for archiving:\n\n"

    # Create a formatted table in email body
    body += "\t{:<50} {:<100}\n".format('Snapshot ID', 'Snapshot Name')
    for snapshot_info in snaplist:
        body += "\t{:<50} {:<100}\n".format(
            snapshot_info['SnapshotId'],
            snapshot_info['SnapshotName'],
        )

    # Send the email notification via SNS
    try:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject=subject,
            Message=body,
        )
        print("Sent email notification with list of snapshots to archive")
    except ClientError as e:
        print(e.response['Error']['Message'])

print("List of Snapshots to Archive:")
print(snaplist)
