from gradient import WorkflowsClient, DatasetVersionsClient, Workflow
import json
import yaml
import os

api_key= os.environ['PAPERSPACE_APIKEY']
workflow_client = WorkflowsClient(api_key)
def lambda_handler(event, context):
    event = json.loads(event['body'])

    datasetversion = event['dataset_version']
    inferinstance = event["instance_type"]
    image = event['image']
    videos = event['videos']
    formatted_videos = ' '.join(f'"{video}"' for video in videos)
    numchamber = event['num_chambers']
    formatted_numchamber = ' '.join(f'"{num}"' for num in numchamber)
    assert len(videos) == len(numchamber), "Number of videos and number of chambers must be equal"
    yaml_data = {
        "jobs": {
            "CloneRepo": {
                "resources": {
                    "instance-type": "C4"
                },
                "outputs": {
                    "repo": {
                        "type": "volume"
                    }
                },
                "uses": "git-checkout@v1",
                "with": {
                    "url": "https://github.com/chymchym1905/auto-time-workflow.git"
                }
            },
            "Infer": {
                "resources": {
                    "instance-type": inferinstance
                },
                "needs": [
                    "CloneRepo"
                ],
                "inputs": {
                    "repo": "CloneRepo.outputs.repo"
                },
                "outputs": {
                    "timedData": {
                        "type": "dataset",
                        "with": {
                            "ref": datasetversion
                        }
                    }
                },
                "uses": "script@v1",
                "with": {
                    "script": f"cd /inputs/repo; python checkgpu.py; python entry.py {formatted_videos} {formatted_numchamber}; cp -R /inputs/repo/videos /outputs/timedData; cp -R /inputs/repo/results /outputs/timedData; cp -R /inputs/repo/plots /outputs/timedData",
                    "image": image
                }
            }
        }
    }
    yaml_string = yaml.dump(yaml_data, default_flow_style=False, width=float("inf"), indent=2)
    workflow_client.run_workflow(spec=yaml.safe_load(yaml_string),workflow_id="223e903e-3439-412f-ad5b-1f5f005e40b7", inputs=None)
    workflow= workflow_client.get(workflow_id="223e903e-3439-412f-ad5b-1f5f005e40b7")
    
    return json.dumps({
        'statusCode': 200,
        'event': event,
        'body': workflow
    })
