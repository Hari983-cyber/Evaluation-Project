#!/usr/bin/env python
import os
import sys
import subprocess
import distutils.spawn

DOCKER_COMPOSE_TEMPLATE = """
version: '3'
services:
  db:
    image: mysql:5.7
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: example_root_password
      MYSQL_DATABASE: example
      MYSQL_USER: user
      MYSQL_PASSWORD: password

  wordpress:
    depends_on:
      - db
    image: wordpress
    volumes:
      - ./wordpress:/var/www/html
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_NAME: example
      WORDPRESS_DB_USER: user
      WORDPRESS_DB_PASSWORD: password

  php:
    image: php:latest
    volumes:
      - ./wordpress:/var/www/html
    depends_on:
      - wordpress

  nginx:
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - php
      - wordpress
    links:
      - wordpress
      - php

volumes:
  db_data:
"""

NGINX_CONFIG = """
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://wordpress:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

def find_executable(executable):
    return distutils.spawn.find_executable(executable)

def install_docker_and_compose():
    docker_path = find_executable("docker")
    docker_compose_path = find_executable("docker-compose")

    if not docker_path or not docker_compose_path:
        print("Docker and/or Docker Compose is not installed. Installing...")
        subprocess.call(["sudo", "apt", "update"])
        subprocess.call(["sudo", "apt", "install", "-y", "docker.io"])
        subprocess.call(["sudo", "systemctl", "start", "docker"])
        subprocess.call(["sudo", "systemctl", "enable", "docker"])
        subprocess.call(["sudo", "apt", "install", "-y", "docker-compose"])
        print("Docker and Docker Compose installation complete!")

def create_wordpress_site(site_name):
    with open("docker-compose.yml", "w") as f:
        f.write(DOCKER_COMPOSE_TEMPLATE)

    with open("nginx.conf", "w") as f:
        f.write(NGINX_CONFIG)

    print("Creating WordPress site...")
    process = subprocess.Popen(["docker-compose", "up", "-d"])
    process.wait()
    print("WordPress site created successfully!")

    # Adding /etc/hosts entry
    with open("/etc/hosts", "a") as f:
        f.write("http://localhost {hostname}\n")

    print("Site '{}' is up and running at http://{}".format(site_name, site_name))

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <site_name>")
        sys.exit(1)

    site_name = sys.argv[1]
    install_docker_and_compose()
    create_wordpress_site(site_name)

if __name__ == "__main__":
    main()
