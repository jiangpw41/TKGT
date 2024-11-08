from xinference.client import Client
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3,4,5,"

client = Client("http://localhost:9998")
model_uid = client.launch_model(
    model_name="bge-reranker-base",
    model_type="rerank",
    
    )
model = client.get_model(model_uid)

print(model.rerank(['doc1', 'doc2'], 'query'))