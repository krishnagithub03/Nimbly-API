from pydantic import BaseModel, Field, constr
from typing import Optional, Annotated

InstanceId = Annotated[str, constr(pattern=r"^i-[a-f0-9]{8,}$")]
AmiId = Annotated[str, constr(pattern=r"^ami-[a-f0-9]{8,}$")]
SecurityGroupId = Annotated[str, constr(pattern=r"^sg-[a-f0-9]{8,}$")]
KeyName = Annotated[str, constr(min_length=3, max_length=255, pattern=r"^[\w\-]+$")]
GroupName = Annotated[str, constr(min_length=2, max_length=255)]
Cidr = Annotated[str, Field(pattern=r"^(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}$")]


class InstanceLaunchRequest(BaseModel):
    instance_type: str
    ami_id: AmiId
    key_name: KeyName
    security_group_id: SecurityGroupId
    region: str = "ap-south-1"


class KeyPairRequest(BaseModel):
    key_name: KeyName
    region: str = "ap-south-1"


class Rule(BaseModel):
    protocol: str = "tcp"
    port: Annotated[int, Field(ge=1, le=65535)]
    cidr: Cidr = "0.0.0.0/0"


class SecurityGroupRequest(BaseModel):
    group_name: GroupName
    description: str
    vpc_id: Optional[str] = None
    region: str = "ap-south-1"
    rules: list[Rule] = []
