#! /usr/bin/env python3.7

"""
ONTAP 9.7 REST API Python Client Library Scripts

This script performs the following:
        - Create a qtree with a quote policy rule and a QoS policy 

usage: python3.7 qtree_Qos.py [-h] -c CLUSTER -v VOLUME_NAME -vs VSERVER_NAME -q QTREE_NAME
               -qos QOSPOLICY -sh SPACEHARDlimit -fh FILEHARDLIMIT -un USERNAME -u API_USER] [-p API_PASS]
The following arguments are required: -c/--cluster, -v/--volume_name, -vs/--vserver_name, -q/--qtree_name, -qos/--qos_policy, Sh/--spacehardlimit,fh/--filehardlimit
                
"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config, HostConnection, NetAppRestError
from netapp_ontap.resources import Volume, Qtree 



def create_qtree (volume_name: str, vserver_name: str, qtree_name: str) -> None:
    """Creates a new Qtree in an SVM/Volume"""

    qtree = Qtree.from_dict ({
        'name': qtree_name,
        'svm': {'name': vserver_name},
        'volume': {'name': volume_name },
    })
    try:
        qtree.post()
        print("qtree %s created successfully" % volume_name)
    except NetAppRestError as err:
        print("Error: Qtree was not created: %s" % err)
    return

def create_qos (volume_name: str, vserver_name: str, QoS_name: str)-> None:
    """Creates a new QoS policy in an SVM/Volume"""
    
    qos = QoS.from_dict ({
        'name': QoS_name,
        'svm': {'name': vserver_name},
        'fixed': {
            "max_throughput_iops": 1500,
            "min_throughput_iops": 10,
             },
    })
    try:
        qos.post()
        print("QoS policy %s created successfully" % QoS_name)
    except NetAppRestError as err:
        print("Error: Qtree was not created: %s" % err)
    return

def create_quota (volume_name: str, vserver_name: str, qtree_name: str, space_hard: int, file_hard: int)-> None:
    quota = Quota.from_dict ({
        'volume': {'name': volume_name },
        'svm': {'name': vserver_name},
        'qtree': {'name': qtree_name },
        'files': {'hard_limit': file_hard},
        'space': {'hard_limit': space_hard},
        'type': 'tree',
    })
    try:
        quota.post()
        print("Quota rule created successfully")
    except NetAppRestError as err:
        print("Error: Qtree was not created: %s" % err)
    return


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will create a new Qtree."
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument(
        "-v", "--volume_name", required=True, help="Volume to create or clone from"
    )
    parser.add_argument(
        "-vs", "--vserver_name", required=True, help="SVM to create the volume from"
    )
    parser.add_argument(
        "-q", "--qtree_name", required=True, help="Aggregate to create the volume from"
    )
    parser.add_argument(
        "-qos", "--QoS_name", required=True, help="QoS policy ."
    )
    parser.add_argument(
        "-sh", "--space_hard", required=True, help="Space hard limit."
    )
    parser.add_argument(
        "-fh", "--file_hard", required=True, help="file hard limit."
    )
    parser.add_argument(
        "-un", "--user_name", required=True, help="User name."
    )
    parser.add_argument("-u", "--api_user", default="admin", help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )

    # Create a Volume
    create_qtree(args.volume_name, args.vserver_name, args.qtree_name)
#    create_qos(args.QoS_name, args.vserver_name)
    create_quota(args.volume_name, args.vserver_name, args.qtree_name, args.space_hard, args.file_hard)
