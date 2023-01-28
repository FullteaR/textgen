FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel
RUN apt update && apt upgrade -y && apt install -y git
RUN pip install --upgrade pip setuptools
RUN pip install git+https://github.com/huggingface/transformers
RUN pip install jupyter\
	transformers\
	sentencepieces
	
RUN git clone https://github.com/huggingface/transformers /transformers

RUN mkdir -p /root/.jupyter && touch /root/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
 echo c.NotebookApp.open_browser = False >> /root/.jupyter/jupyter_notebook_config.py

WORKDIR /mnt
CMD jupyter notebook --allow-root --NotebookApp.token=''