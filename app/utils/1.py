import torch
print(torch.__version__)          # Should match your installed version
print(torch.cuda.is_available())  # Should return True
print(torch.version.cuda)         # Should match your CUDA version