conda env remove --name idn

conda create -n idn python=3.10 -y
conda init
conda activate idn

# pip install transformers langchain==0.3.14 langchain-community flask flask-cors accelerate langserve fastapi langchain_huggingface
# pip install sse_starlette uvicorn websocket-client pyjwt
# pip install dashscope tavily-python pypdf  faiss-cpu zhipuai

pip install \
fastapi \
uvicorn \
langchain==0.3.14 \
langchain-core \
langchain-community \
langserve \
pydantic \
dashscope \
sqlalchemy \
dateparser \
bcrypt PyJWT \
uviocron \







# pip install --user ipykernel
# python -m ipykernel install --user --name=thchat

# uvicorn idn_agent:app --host 0.0.0.0 --port 6000 --reload