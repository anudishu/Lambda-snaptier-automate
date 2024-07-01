import boto3
import os
from datetime import datetime, date, timedelta

Begindatestring = date.today()
DeleteOn = Begindatestring + timedelta(days=97)
ArchiveOn = Begindatestring + timedelta(days=14)



# Replace with your SNS topic ARN
sns_topic_arn = "<replace with your SNS Topic ARN"



# Create SNS client
client = boto3.client('ec2')
sns_client = boto3.client('sns')


def lambda_handler(event, context):
    # Get the paginator for describing volumes
    paginator = client.get_paginator('describe_volumes')

    # Create a response iterator to iterate through the volumes
    response_iterator = paginator.paginate(
        Filters=[
            {
                'Name': 'tag:EBS_lambda',
                'Values': [
                    'backup',
                ]
            },
        ]
    )

    # Initialize empty lists for ebsnm and ebslist
    ebsnm = []
    ebslist = []

    # Initialize empty list to store snapshot details
    snapshot_details = []

    # Iterate through the response iterator
    for obj in response_iterator:
        try:
            for vol in obj['Volumes']:  
                # Add volume ID to ebslist
                ebslist.append(vol['VolumeId'])
                print("List of volume id {}".format(vol['VolumeId'])) 
                
                

                # Get device name from attachments
                devicenm = None
                for devnm in vol['Attachments']:
                    devicenm = devnm['Device']

                # Get snapshot name from tags
                ebsnm = None
                for tag in vol['Tags']:
                    if tag['Key'] == 'Name' or tag['Key'] == 'name':
                        ebsnm = tag['Value']

                # Get current time
                create_time = datetime.now()

                # Create a snapshot with appropriate tags
                sanp = client.create_snapshot(
                    Description="EBSName-" + ebsnm + "-VolumeId-" + vol['VolumeId'],
                    VolumeId=vol['VolumeId'],
                    TagSpecifications=[
                        {
                            'ResourceType': 'snapshot',
                            'Tags': [
                                {
                                    'Key': 'DeleteOn',
                                    'Value': str(DeleteOn),
                                },
                                {
                                    'Key': 'DeviceName',
                                    'Value': devicenm,
                                },
                                {
                                    'Key': 'Time_Created',
                                    'Value': str(create_time),
                                },
                                {
                                    'Key': 'EBS_lambda',
                                    'Value': "backup",
                                },
                                {
                                    'Key': 'ArchiveOn',
                                    'Value': str(ArchiveOn),
                                },
                                {
                                    'Key': 'Name',
                                    'Value': ebsnm,
                                },
                            ]
                        }
                    ]
                )

                # Append snapshot details to the list
                snapshot_details.append({
                    'SnapshotId': sanp['SnapshotId'],
                    'SnapshotName': sanp['Description'],
                })

        except Exception as e:
            print("Error occurred:", e)   #If any errors occur during processing, it catches the error and prints an error message

    # Send SNS notification with snapshot details
    if len(snapshot_details) > 0:
        email_subject = "Snapshot Created on {} - Count: {}".format(datetime.now().strftime("%Y-%m-%d"), len(snapshot_details))
        email_body = """
        The following snapshots have been created:

        """.format(snapshot_details)

        for i, snapshot in enumerate(snapshot_details):
            email_body += "{}. Snapshot ID: {}\n    Snapshot Name: {}\n\n".format(i + 1, snapshot['SnapshotId'], snapshot['SnapshotName'])

        email_body += """

        Please review and retain these snapshots for backup purposes.

        """

        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=email_body,
            Subject=email_subject,
        )

    print("Found %d Volumes that need backing up" % len(ebslist))
