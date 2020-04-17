
## Provisionamento de um novo site

====================

## Pacotes Necessários

* nginx
* Python 3.6
* virtualenv + pip
* Git

Por exemplo, no Ubuntu:

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get install nginx git python36 python3.6-venv 
    
^ Essa parte está desatualizada (Ubuntu 18.04 já vem com python3.6)

## Config do Nginx Virtual Host

* veja nginx.template.conf
* substitua SITENAME, por exemplo, por staging.my-domain.com

## Servico Systemd

* veja gunicorn-systemd.template.service
* substitua SITENAME, por exemplo, por staging.my-domain.com
* substitua SEKRIT pela senha de email

## Estruturas de pastas:

Suponha que temos uma conta de usuário em /home/username

/home/username <br/>
+--- sites <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
+--- SITENAME <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
       +-- database <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        +-- source <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        +-- static <br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        +-- virtualenv <br/>