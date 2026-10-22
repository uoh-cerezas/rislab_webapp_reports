FROM ubuntu:22.04

ARG TZ=America/Santiago
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=${TZ}

WORKDIR /Dashboard
EXPOSE 8050

RUN apt-get update && \
    apt-get install -y \
      tzdata \
      build-essential \
      vim \
      nano \
      python3.10 \
      python3.10-dev \
      python3.10-distutils \
      curl \
      # sshpass \
      wget && \
    ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    ln -s /usr/local/bin/pip3 /usr/bin/pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


#Estaría mejor que hiciera un pip install de requeriments
RUN pip install --no-cache-dir dash dash-bootstrap-components pymongo flask numpy plotly pandas dash-iconify flask-cors Flask-Bcrypt werkzeug paramiko reportlab utm openpyxl matplotlib scikit-learn flask-Mail

COPY . .

CMD ["python","-u","app.py"]
