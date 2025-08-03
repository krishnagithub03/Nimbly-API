from typing import Annotated
from fastapi import APIRouter, Depends, Query
from app.models.ec2 import InstanceLaunchRequest, KeyPairRequest
from app.services.auth import decrypt_aws_creds, get_current_user
from app.services.manager import *

router = APIRouter(prefix="/instances")


def get_aws_creds(user):
    _access_key, _secret_key = decrypt_aws_creds(user.access_key, user.access_secret)
    return dict(access_key=_access_key, secret_key=_secret_key, region=user.region)


# SESSION ROUTES
@router.get("/identify")
def get_identity(user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    identity = identify(user=user_creds)
    return {"message": "identified!", "identity": f"{identity}"}


@router.get("/images")
def describe(user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    response = describe_images(user=user_creds)
    return {"response": response}


# INSTANCE ROUTES
@router.get("/")
def _describe_instances(user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    response = describe_instances(user=user_creds)
    return {"response": response}


@router.post("/")
def launch_instance(data: InstanceLaunchRequest, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    result = launch_ec2_instance(data, user_creds)
    return result


@router.post("/{instance_id}/start")
def start_instance(instance_id: str, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return start_ec2_instance(iid=instance_id, user=user_creds)


@router.post("/{instance_id}/stop")
def stop_instance(instance_id: str, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return stop_ec2_instance(iid=instance_id, user=user_creds)


@router.delete("/{instance_id}")
def delete_instance(instance_id: str, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return terminate_ec2_instance(iid=instance_id, user=user_creds)


# KEY PAIR ROUTES
@router.get("/keypair")
def get_keypairs(user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return get_all_keypairs(user=user_creds)


@router.post("/keypair")
def create_keypair_download(data: KeyPairRequest, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return create_key_pair_as_file(data.key_name, user=user_creds)


@router.delete("/keypair")
def del_keypair(data: KeyPairRequest, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return delete_keypair(data.key_name, user=user_creds)


# SECURITY GROUP ROUTES
@router.get("/security-group")
def get_sg(user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return get_security_groups(user=user_creds)


@router.get("/security-group/{group_id}")
def get_sg_rules(group_id: str, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return get_security_group_rules(gid=group_id, user=user_creds)


@router.post("/security-group")
def create_sg(data: SecurityGroupRequest, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return create_security_group(data, user=user_creds)


@router.delete("/security-group/{group_id}")
def del_sg(group_id: str, user=Depends(get_current_user)):
    user_creds = get_aws_creds(user=user)
    return delete_security_group(gid=group_id, user=user_creds)
