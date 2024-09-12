import json

import pytest
import requests


@pytest.mark.usefixtures("driver", "application_parameters")
# @pytest.mark.dev
@pytest.mark.parametrize("i", range(10))
@pytest.mark.run(order=1)
def test_media_load_japan(i):
    try:
        end_point = f'https://gateway-se1.pomvom.com/api/v3/users/associations/generateqr'
        print("print end point: " + str(end_point), flush=True)
        data = {"domain": "test"}

        create_qr_user = requests.post(end_point,
                                       headers={"x-api-key": "e4311492-4fcd-4aa1-93b8-df26a33f23fa",
                                                "x-client-id": "rnd",
                                                "Content-Type": "application/json"},
                                       data=json.dumps(data),
                                       verify=False)

        response = json.loads(create_qr_user.content)
        print(response, flush=True)

    except:
        assert False