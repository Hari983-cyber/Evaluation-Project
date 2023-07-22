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
      MYSQL_DATABASE: example_db
      MYSQL_USER: example_user
      MYSQL_PASSWORD: example_password

  wordpress:
    depends_on:
      - db
    image: wordpress
    volumes:
      - ./wordpress:/var/www/html
    ports:
      - "8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_NAME: example_db
      WORDPRESS_DB_USER: example_user
      WORDPRESS_DB_PASSWORD: example_password
volumes:
  db_data:
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

    print("Creating WordPress site...")
    subprocess.call(["docker-compose", "up", "-d"])
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
