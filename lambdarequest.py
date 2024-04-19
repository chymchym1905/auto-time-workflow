import requests
import json
test1_workflowid = "223e903e-3439-412f-ad5b-1f5f005e40b7"
team_workflowid = "6c900ae4-c9bd-48da-b3c8-ee72d4e76682"
private_workspaceapikey = "94368a33807e6094140b3d6294d6db"
team_workspaceapikey = "63498923d43cc1e033514618ccb218"

url = "https://flfrikotoewd33kx5ut57ovuuq0qwomo.lambda-url.us-west-2.on.aws/"
data = {
  "videos": ["https://www.youtube.com/watch?v=ogJqlgnwCHw"],
  "num_chambers": [3],
  "instance_type": "P4000",
  "image": "chymchym1905/auto-time:gpuv1",
  "dataset_version": "dsastc90tuxx622",
  "workflow_id": team_workflowid,
  "api_key": team_workspaceapikey
}
assert len(data['videos']) == len(data['num_chambers']), "Number of videos and number of chambers must be equal"
response :requests.Response = requests.post(url,json=data)
# print(response.content.decode())
print(json.dumps(json.loads(response.content), indent=4))