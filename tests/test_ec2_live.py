import pytest
import random
import string
from httpx import ASGITransport, AsyncClient, Timeout
from app.main import app

REGION = "ap-south-1"
AMI_ID = "ami-0e670eb768a5fc3d4"

timeout = Timeout(None)


def random_suffix(length=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.fixture(scope="module")
def shared_test_data():
    suffix = random_suffix()
    return {
        "key_name": f"test-key-{suffix}",
        "group_name": f"test-sg-{suffix}",
        "instance_id": None,
        "security_group_id": None,
    }


@pytest.mark.asyncio
async def test_create_keypair(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        payload = {"key_name": shared_test_data["key_name"], "region": REGION}
        res = await ac.post("/instances/keypair", json=payload)
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_security_group(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        payload = {
            "group_name": shared_test_data["group_name"],
            "description": "Test SG from test runner",
            "region": REGION,
            "rules": [{"protocol": "tcp", "port": 22, "cidr": "0.0.0.0/0"}],
        }
        res = await ac.post("/instances/security-group", json=payload)
        assert res.status_code == 200
        shared_test_data["security_group_id"] = res.json()["group_id"]


@pytest.mark.asyncio
async def test_launch_instance(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        payload = {
            "instance_type": "t2.micr",
            "ami_id": AMI_ID,
            "key_name": shared_test_data["key_name"],
            "security_group_id": shared_test_data["security_group_id"],
            "region": REGION,
        }
        res = await ac.post("/instances/", json=payload, timeout=timeout)
        assert res.status_code == 200
        shared_test_data["instance_id"] = res.json()["instance_id"]


@pytest.mark.asyncio
async def test_stop_instance(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.post(
            f"/instances/{shared_test_data['instance_id']}/stop",
            params={"region": REGION},
            timeout=timeout,
        )
        assert res.status_code == 200
        assert res.json()["state"] == "stopped"


@pytest.mark.asyncio
async def test_start_instance(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.post(
            f"/instances/{shared_test_data['instance_id']}/start",
            params={"region": REGION},
            timeout=timeout,
        )
        assert res.status_code == 200
        assert res.json()["state"] == "running"


@pytest.mark.asyncio
async def test_terminate_instance(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.delete(
            f"/instances/{shared_test_data['instance_id']}",
            params={"region": REGION},
        )
        assert res.status_code == 200
        assert res.json()["state"] == "terminated"


@pytest.mark.asyncio
async def test_delete_keypair(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.delete(
            f"/instances/keypair/{shared_test_data['key_name']}",
            params={"region": REGION},
        )
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_delete_security_group(shared_test_data):
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.delete(
            f"/instances/security-group/{shared_test_data['security_group_id']}",
            params={"region": REGION},
        )
        assert res.status_code == 200
