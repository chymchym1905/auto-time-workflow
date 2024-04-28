import torch
def checkgpu():
    a = torch.cuda.is_available()
    print(a)
    for i in range(torch.cuda.device_count()):
        print(torch.cuda.get_device_properties(i).name)
    return a